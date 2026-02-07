"""
Rooms app views.
Handles room listing, creation, and detail pages.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import Room, RoomMembership
import json


def landing_view(request):
    """
    Landing page for non-authenticated users.
    Shows intro to Virtual Cafe with call to action.
    """
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'landing.html')


@login_required
def home_view(request):
    """
    Home dashboard showing all available rooms.
    Users must be logged in to see this page.
    """
    from tracker.models import StudySession
    from django.db.models import Sum
    from datetime import datetime, timedelta
    from django.contrib.auth.models import User
    
    # Clean up expired rooms (excluding the global room)
    expired_rooms = Room.objects.filter(
        expires_at__lte=timezone.now()
    ).exclude(room_code='GLOBAL')
    expired_count = expired_rooms.count()
    if expired_count > 0:
        expired_rooms.delete()
        messages.info(request, f'{expired_count} empty room(s) expired and removed.')
    
    # Get all active rooms (not expired)
    rooms = Room.objects.filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )
    
    # Get search query from GET parameters
    search_query = request.GET.get('search', '').strip()
    
    # Apply search filter if provided
    if search_query:
        # Search in room name and description
        rooms = rooms.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Annotate with member count for display
    rooms = rooms.annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).select_related('created_by')
    
    # Get rooms the current user is a member of
    user_rooms = Room.objects.filter(memberships__user=request.user, memberships__is_active=True)
    
    # Get active study sessions (users who studied in the last 24 hours)
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    
    # Get recent study sessions grouped by user
    recent_sessions = StudySession.objects.filter(
        created_at__gte=yesterday
    ).select_related('user', 'user__profile').values('user').annotate(
        total_minutes=Sum('minutes')
    ).order_by('-total_minutes')[:4]  # Top 4 active users
    
    # Enrich with user details
    active_sessions = []
    for session in recent_sessions:
        user = User.objects.select_related('profile').get(id=session['user'])
        active_sessions.append({
            'user': user,
            'minutes': session['total_minutes'],
            'hours': session['total_minutes'] // 60,
            'remaining_minutes': session['total_minutes'] % 60,
        })
    
    # Get current user's weekly statistics
    week_ago = today - timedelta(days=7)
    user_week_sessions = StudySession.objects.filter(
        user=request.user,
        created_at__gte=week_ago
    )
    
    # Calculate weekly total
    week_total = user_week_sessions.aggregate(total=Sum('minutes'))['total'] or 0
    
    # Calculate completion percentage (40 hours = 2400 minutes = 100%)
    weekly_goal = 2400  # 40 hours in minutes
    completion_percent = min(100, int((week_total / weekly_goal) * 100))
    
    # Get daily breakdown for the last 7 days
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_sessions = user_week_sessions.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        )
        day_total = day_sessions.aggregate(total=Sum('minutes'))['total'] or 0
        
        daily_stats.append({
            'day': day.strftime('%a'),  # Mon, Tue, etc.
            'minutes': day_total,
            'hours': round(day_total / 60, 1)
        })
    
    # Get online friends (users who were active in last 30 minutes)
    thirty_mins_ago = today - timedelta(minutes=30)
    online_users = User.objects.filter(
        Q(study_sessions__created_at__gte=thirty_mins_ago) |
        Q(room_memberships__joined_at__gte=thirty_mins_ago)
    ).exclude(id=request.user.id).distinct().select_related('profile')[:12]
    
    context = {
        'rooms': rooms,
        'user_rooms': user_rooms,
        'search_query': search_query,
        'active_sessions': active_sessions,
        'week_total_minutes': week_total,
        'week_total_hours': round(week_total / 60, 1),
        'completion_percent': completion_percent,
        'daily_stats': json.dumps(daily_stats),
        'online_users': online_users,
    }
    return render(request, 'rooms/home.html', context)


@login_required
def create_room_view(request):
    """
    Create a new study room.
    GET: Display create room form
    POST: Create the room and redirect to room detail
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Validate room name
        if not name or len(name.strip()) == 0:
            messages.error(request, 'Room name is required.')
            return render(request, 'rooms/create_room.html')
        
        # Create the room
        room = Room.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        
        # Automatically add creator as a member
        RoomMembership.objects.create(
            user=request.user,
            room=room,
            is_active=True
        )
        
        messages.success(request, f'Room "{name}" created successfully!')
        return redirect('room_detail', room_code=room.room_code)
    
    # GET request - show form
    return render(request, 'rooms/create_room.html')


@login_required
def global_chat_view(request):
    """
    Global chat room where anyone can join and chat with everyone.
    Creates the global room if it doesn't exist.
    """
    # Get or create the global chat room
    global_room, created = Room.objects.get_or_create(
        room_code='GLOBAL',
        defaults={
            'name': 'Global Chat Room',
            'description': 'A public space where everyone can chat and study together!',
            'created_by': request.user
        }
    )
    
    # If room was just created, set it as not expiring
    if created:
        global_room.expires_at = None
        global_room.save()
    
    # Check if user is already a member
    existing_membership = RoomMembership.objects.filter(
        user=request.user,
        room=global_room
    ).first()
    
    # If already a member, reactivate if needed
    if existing_membership:
        if not existing_membership.is_active:
            existing_membership.is_active = True
            existing_membership.save()
    else:
        # Create new membership
        RoomMembership.objects.create(
            user=request.user,
            room=global_room,
            is_active=True
        )
    
    # Update room activity
    global_room.update_activity()
    
    # Get all active members in the room
    active_members = RoomMembership.objects.filter(
        room=global_room,
        is_active=True
    ).select_related('user')
    
    context = {
        'room': global_room,
        'active_members': active_members,
        'members_count': active_members.count(),
        'is_owner': global_room.created_by == request.user,
        'is_global': True,  # Flag to indicate this is the global room
    }
    return render(request, 'rooms/chat_room.html', context)


@login_required
def room_detail_view(request, room_code):
    """
    Room detail page with chat, video call, timer, and members list.
    This is the main study room interface.
    Checks room capacity and permissions before allowing entry.
    """
    # Get the room or return 404 if not found
    room = get_object_or_404(Room, room_code=room_code)
    
    # Check if room has expired
    if room.is_expired():
        room.delete()
        messages.error(request, 'This room has expired due to inactivity.')
        return redirect('home')
    
    # Check if user is already a member
    existing_membership = RoomMembership.objects.filter(
        user=request.user,
        room=room
    ).first()
    
    # If already a member, reactivate if needed
    if existing_membership:
        if not existing_membership.is_active:
            existing_membership.is_active = True
            existing_membership.save()
    else:
        # Create new membership
        RoomMembership.objects.create(
            user=request.user,
            room=room,
            is_active=True
        )
        
        # Create notification for room owner (if not the owner joining)
        if room.created_by != request.user:
            from notifications.models import Notification
            Notification.create_new_member_notification(
                room_owner=room.created_by,
                new_member=request.user,
                room=room
            )
    
    # Update room activity (clears expiration since user just joined)
    room.update_activity()
    
    # Get all active members in the room
    active_members = RoomMembership.objects.filter(
        room=room,
        is_active=True
    ).select_related('user')
    
    context = {
        'room': room,
        'active_members': active_members,
        'members_count': active_members.count(),
        'is_owner': room.created_by == request.user,
    }
    return render(request, 'rooms/room_detail.html', context)
