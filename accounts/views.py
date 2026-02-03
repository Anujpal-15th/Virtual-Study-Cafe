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
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile


def signup_view(request):
    """
    Handle user registration with email
    GET: Display signup form
    POST: Create new user and log them in
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            # Log the user in automatically
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('home')  # Redirect to home dashboard
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
def edit_profile_view(request):
    """
    Edit current user's profile
    Handles both user account info and profile info in one form
    """
    if request.method == 'POST':
        # Two forms: one for User model, one for UserProfile model
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES,  # Important for file uploads (avatar)
            instance=request.user.profile
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
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
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
