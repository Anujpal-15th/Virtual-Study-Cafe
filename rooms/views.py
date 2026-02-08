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
    Home dashboard showing rooms created by the current user.
    Users must be logged in to see this page.
    """
    from tracker.models import StudySession
    from django.db.models import Sum
    from datetime import datetime, timedelta
    from django.contrib.auth.models import User
    
    # Clean up expired rooms
    expired_rooms = Room.objects.filter(
        expires_at__lte=timezone.now()
    )
    expired_count = expired_rooms.count()
    if expired_count > 0:
        expired_rooms.delete()
        messages.info(request, f'{expired_count} empty room(s) expired and removed.')
    
    # Get all active PUBLIC rooms (visible to everyone, )
    rooms = Room.objects.filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()),
        is_public=True
    ).exclude(room_code='GLOBAL')
    
    # Get search query from GET parameters
    search_query = request.GET.get('search', '').strip()
    
    # Apply search filter if provided
    if search_query:
        # Search in room name and description
        rooms = rooms.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Annotate with member count for display and order by popularity
    rooms = rooms.annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).select_related('created_by').order_by('-member_count', '-created_at')
    
    # Get rooms the current user is a member of (excluding GLOBAL room if it exists)
    user_rooms = Room.objects.filter(
        memberships__user=request.user, 
        memberships__is_active=True
    ).exclude(room_code='GLOBAL').annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).select_related('created_by')
    
    # Get active study sessions (users who studied in the last 24 hours)
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    
    # Get recent study sessions grouped by user (removed - not displayed)
    # active_sessions = []
    
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
        is_public = request.POST.get('is_public') == 'on'  # Checkbox value
        
        # Validate room name
        if not name or len(name.strip()) == 0:
            messages.error(request, 'Room name is required.')
            return render(request, 'rooms/create_room.html')
        
        # Create the room
        room = Room.objects.create(
            name=name,
            description=description,
            created_by=request.user,
            is_public=is_public
        )
        
        # Automatically add creator as a member
        RoomMembership.objects.create(
            user=request.user,
            room=room,
            is_active=True
        )
        
        visibility = "public" if is_public else "private"
        messages.success(request, f'Room "{name}" created successfully as {visibility}!')
        return redirect('room_detail', room_code=room.room_code)
    
    # GET request - show form
    return render(request, 'rooms/create_room.html')


@login_required
def join_room_by_code_view(request):
    """
    Handle joining a room by entering a room code.
    GET: Display join room form
    POST: Join the room by code and redirect to room detail
    """
    if request.method == 'POST':
        room_code = request.POST.get('room_code', '').strip().upper()
        
        # Validate room code
        if not room_code:
            messages.error(request, 'Please enter a room code.')
            return redirect('home')
        
        # Try to find the room
        try:
            room = Room.objects.get(room_code=room_code)
            
            # Check if room has expired
            if room.is_expired():
                room.delete()
                messages.error(request, 'This room has expired due to inactivity.')
                return redirect('home')
            
            # Redirect to room detail (which handles membership creation)
            messages.success(request, f'Joining room "{room.name}"...')
            return redirect('room_detail', room_code=room.room_code)
            
        except Room.DoesNotExist:
            messages.error(request, f'Room with code "{room_code}" not found. Please check the code and try again.')
            return redirect('home')
    
    # GET request - redirect to home
    return redirect('home')


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


@login_required
def delete_room_view(request, room_code):
    """
    Delete a room. Only the room owner can delete their room.
    Returns JSON response for AJAX calls.
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)
    
    # Get the room or return 404
    room = get_object_or_404(Room, room_code=room_code)
    
    # Check if the user is the owner
    if room.created_by != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Only the room owner can delete this room.'
        }, status=403)
    
    # Delete the room (this will cascade delete memberships)
    room_name = room.name
    room.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Room "{room_name}" has been deleted successfully.'
    })
