"""
Accounts app views.
Handles user authentication, profiles, and notifications.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile, EmailVerification


def signup_view(request):
    """
    Handle user registration with email verification
    GET: Display signup form
    POST: Create new user and send verification email
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the new user (but don't log them in yet)
            user = form.save()
            user.is_active = True  # Keep active but require email verification
            user.save()
            
            # Create verification token
            verification = EmailVerification.create_for_user(user)
            
            # Send verification email
            send_verification_email(request, user, verification)
            
            messages.success(
                request, 
                f'Account created! Please check your email ({user.email}) to verify your account.'
            )
            return redirect('verification_sent')
        else:
            # Show form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    GET: Display login form
    POST: Authenticate user and log them in
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Check if email is verified
                if hasattr(user, 'profile') and not user.profile.email_verified:
                    messages.warning(
                        request, 
                        f'Welcome back, {username}! Please verify your email to access all features. '
                        '<a href="/resend-verification/" style="color: white; text-decoration: underline;">Resend verification email</a>'
                    )
                else:
                    messages.success(request, f'Welcome back, {username}!')
                
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout.
    Log out the user and redirect to login page.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request, username=None):
    """
    Display user profile page
    If username is provided, show that user's profile
    Otherwise, show the current logged-in user's profile
    """
    if username:
        # View someone else's profile
        profile_user = get_object_or_404(User, username=username)
    else:
        # View own profile
        profile_user = request.user
    
    # Get or create profile (in case it doesn't exist)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    
    # Calculate additional stats
    from tracker.models import StudySession
    from django.db.models import Sum
    from datetime import date, timedelta
    
    # Get study sessions for this user
    sessions = StudySession.objects.filter(user=profile_user)
    
    # Calculate stats
    total_sessions = sessions.count()
    avg_session_length = sessions.aggregate(avg=Sum('minutes'))['avg'] or 0
    
    # Last 7 days activity
    seven_days_ago = date.today() - timedelta(days=7)
    recent_minutes = sessions.filter(
        created_at__date__gte=seven_days_ago
    ).aggregate(total=Sum('minutes'))['total'] or 0
    
    # Get user's rooms
    from rooms.models import Room
    user_rooms = Room.objects.filter(created_by=profile_user)[:5]  # Latest 5 rooms
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_own_profile': request.user == profile_user,
        'total_sessions': total_sessions,
        'avg_session_length': round(avg_session_length, 1) if avg_session_length else 0,
        'recent_minutes': recent_minutes,
        'user_rooms': user_rooms,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
@login_required
def edit_profile_view(request):
    """
    Edit current user's profile
    Handles both user account info and profile info in one form
    """
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Two forms: one for User model, one for UserProfile model
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES,  # Important for file uploads (avatar)
            instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to own profile
        else:
            # Show validation errors
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show forms with current data
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def notifications_view(request):
    """
    Display all notifications for the current user
    Shows unread notifications first
    """
    from notifications.models import Notification
    
    # Get all notifications for this user
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Separate read and unread
    unread_notifications = notifications.filter(is_read=False)
    read_notifications = notifications.filter(is_read=True)[:20]  # Last 20 read notifications
    
    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'unread_count': unread_notifications.count(),
    }
    
    return render(request, 'accounts/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a single notification as read (AJAX endpoint)
    Returns JSON response
    """
    from notifications.models import Notification
    
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.mark_as_read()
        
        # Return updated unread count
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    
    return JsonResponse({'success': False}, status=400)


@login_required
def mark_all_notifications_read(request):
    """
    Mark all notifications as read (AJAX endpoint)
    """
    from notifications.models import Notification
    from django.utils import timezone
    
    if request.method == 'POST':
        # Update all unread notifications for this user
        Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })
    
    return JsonResponse({'success': False}, status=400)


# ========================================
# API ENDPOINTS FOR PROFILE
# ========================================

@login_required
def api_get_profile(request):
    """
    API endpoint to get current user's profile data
    Returns JSON with all profile information
    """
    try:
        user = request.user
        profile = user.profile
        
        # Calculate additional stats
        from tracker.models import StudySession
        from django.db.models import Sum, Count
        
        total_sessions = StudySession.objects.filter(user=user).count()
        total_minutes = StudySession.objects.filter(
            user=user, 
            session_type='focus'
        ).aggregate(Sum('minutes'))['minutes__sum'] or 0
        
        data = {
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.strftime('%Y-%m-%d'),
            },
            'profile': {
                'avatar_url': profile.avatar.url if profile.avatar else None,
                'bio': profile.bio,
                'timezone': profile.timezone,
                'total_study_minutes': profile.total_study_minutes,
                'study_streak': profile.study_streak,
                'longest_streak': profile.longest_streak,
                'total_xp': profile.total_xp,
                'level': profile.level,
            },
            'stats': {
                'total_sessions': total_sessions,
                'total_minutes': total_minutes,
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def api_update_profile(request):
    """
    API endpoint to update current user's profile
    Accepts JSON or form-data (for file uploads)
    """
    if request.method != 'POST' and request.method != 'PUT':
        return JsonResponse({
            'success': False,
            'error': 'Only POST/PUT requests allowed'
        }, status=405)
    
    try:
        import json
        from django.core.files.storage import default_storage
        
        user = request.user
        profile = user.profile
        
        # Check if it's JSON or form-data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Update User model fields
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                # Check if username is already taken
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Username already taken'
                    }, status=400)
                user.username = new_username
        
        if 'email' in data:
            new_email = data['email'].strip()
            if not new_email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is required'
                }, status=400)
            user.email = new_email
        
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        
        user.save()
        
        # Update Profile model fields
        if 'bio' in data:
            profile.bio = data['bio'].strip()[:500]  # Max 500 chars
        
        if 'timezone' in data:
            profile.timezone = data['timezone']
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            
            # Validate file size (max 2MB)
            if avatar_file.size > 2 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'Avatar file size must be less than 2MB'
                }, status=400)
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if avatar_file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'error': 'Avatar must be a JPG, PNG, or GIF image'
                }, status=400)
            
            # Delete old avatar if exists
            if profile.avatar:
                try:
                    default_storage.delete(profile.avatar.path)
                except:
                    pass
            
            profile.avatar = avatar_file
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'profile': {
                'avatar_url': profile.avatar.url if profile.avatar else None,
                'bio': profile.bio,
                'timezone': profile.timezone,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ===== EMAIL VERIFICATION VIEWS =====

def send_verification_email(request, user, verification):
    """
    Send verification email to user with verification link
    """
    verification_url = request.build_absolute_uri(
        reverse('verify_email', args=[verification.token])
    )
    
    subject = 'Verify Your VirtualCafe Account'
    html_message = render_to_string('accounts/email_verification.html', {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'VirtualCafe',
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def verification_sent_view(request):
    """
    Display after signup - tells user to check email
    """
    return render(request, 'accounts/verification_sent.html')


def verify_email_view(request, token):
    """
    Handle email verification link clicks
    Verifies the token and activates the user account
    """
    try:
        verification = get_object_or_404(EmailVerification, token=token)
        
        if verification.verified:
            messages.info(request, 'Your email has already been verified. You can log in.')
            return redirect('login')
        
        if verification.is_expired():
            messages.error(
                request, 
                'This verification link has expired. Please request a new one.'
            )
            return redirect('resend_verification')
        
        # Mark as verified
        verification.verified = True
        verification.save()
        
        # Update user profile
        user = verification.user
        if hasattr(user, 'profile'):
            from django.utils import timezone
            user.profile.email_verified = True
            user.profile.email_verified_at = timezone.now()
            user.profile.save()
        
        messages.success(
            request, 
            'Email verified successfully! You can now log in and access all features.'
        )
        return redirect('login')
        
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('login')


def resend_verification_view(request):
    """
    Allow user to request a new verification email
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            # Use filter().first() to handle multiple users with same email
            user = User.objects.filter(email=email).first()
            
            if not user:
                # Don't reveal whether email exists for security
                messages.info(
                    request, 
                    'If an account exists with that email, a verification link will be sent.'
                )
                return redirect('resend_verification')
            
            # Check if already verified
            if hasattr(user, 'profile') and user.profile.email_verified:
                messages.info(request, 'Your email is already verified. You can log in.')
                return redirect('login')
            
            # Invalidate old tokens
            EmailVerification.objects.filter(user=user, verified=False).update(verified=True)
            
            # Create new verification token
            verification = EmailVerification.create_for_user(user)
            
            # Send new email
            if send_verification_email(request, user, verification):
                messages.success(
                    request, 
                    f'A new verification email has been sent to {email}. Please check your inbox.'
                )
            else:
                messages.error(request, 'Failed to send email. Please try again later.')
            
        except Exception as e:
            # Generic error handling
            messages.error(request, 'An error occurred. Please try again later.')
        
        return redirect('resend_verification')
    
    return render(request, 'accounts/resend_verification.html')


@login_required
def check_verification_status(request):
    """
    API endpoint to check if user's email is verified
    """
    is_verified = False
    if hasattr(request.user, 'profile'):
        is_verified = request.user.profile.email_verified
    
    return JsonResponse({
        'email_verified': is_verified,
        'email': request.user.email
    })

