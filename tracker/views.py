"""
Tracker app views.
Handles study progress tracking and saving study sessions.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import StudySession, Achievement
from rooms.models import Room
from django.contrib.auth.models import User


@login_required
def progress_view(request):
    """
    Display user's study progress and statistics.
    Shows today's total, this week's total, and last 7 days breakdown.
    """
    user = request.user
    now = timezone.now()
    today = now.date()
    
    # Calculate today's total minutes
    today_sessions = StudySession.objects.filter(
        user=user,
        created_at__date=today
    )
    today_total = today_sessions.aggregate(Sum('minutes'))['minutes__sum'] or 0
    
    # Calculate this week's total minutes
    week_start = today - timedelta(days=today.weekday())  # Monday of current week
    week_sessions = StudySession.objects.filter(
        user=user,
        created_at__date__gte=week_start
    )
    week_total = week_sessions.aggregate(Sum('minutes'))['minutes__sum'] or 0
    
    # Get last 7 days data for chart
    last_7_days = []
    for i in range(6, -1, -1):  # 6 days ago to today
        day = today - timedelta(days=i)
        day_sessions = StudySession.objects.filter(
            user=user,
            created_at__date=day
        )
        day_total = day_sessions.aggregate(Sum('minutes'))['minutes__sum'] or 0
        last_7_days.append({
            'date': day.strftime('%a'),  # Mon, Tue, etc.
            'minutes': day_total
        })
    
    # Get recent sessions for display
    recent_sessions = StudySession.objects.filter(user=user)[:10]
    
    context = {
        'today_total': today_total,
        'week_total': week_total,
        'last_7_days': last_7_days,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'tracker/progress.html', context)


@login_required
def save_session_view(request):
    """
    Save a completed study session.
    Called via POST when Pomodoro timer completes.
    """
    if request.method == 'POST':
        minutes = request.POST.get('minutes')
        room_code = request.POST.get('room_code', '')
        
        try:
            minutes = int(minutes)
            if minutes <= 0:
                raise ValueError("Minutes must be positive")
            
            # Get room if room_code provided
            room = None
            if room_code:
                try:
                    room = Room.objects.get(room_code=room_code)
                except Room.DoesNotExist:
                    pass
            
            # Create study session
            session = StudySession.objects.create(
                user=request.user,
                room=room,
                minutes=minutes,
                ended_at=timezone.now()
            )
            
            # Update user profile stats (study streak and total minutes)
            user_profile = request.user.profile
            user_profile.update_study_stats(minutes)
            
            # Check for study milestones and create notifications
            from notifications.models import Notification
            Notification.create_study_milestone(request.user, user_profile.total_study_minutes)
            
            messages.success(request, f'Study session of {minutes} minutes saved!')
        
        except (ValueError, TypeError):
            messages.error(request, 'Invalid minutes value.')
        
        # Redirect back to room or progress page
        if room_code:
            return redirect('room_detail', room_code=room_code)
        return redirect('progress')
    
    return redirect('home')


@login_required
def leaderboard_view(request):
    """
    Display the leaderboard showing top users by study time.
    """
    period = request.GET.get('period', 'alltime')
    now = timezone.now()
    
    # Determine date filter based on period
    if period == 'today':
        start_date = now.date()
        period_label = "Today"
    elif period == 'week':
        start_date = now.date() - timedelta(days=now.weekday())
        period_label = "This Week"
    elif period == 'month':
        start_date = now.date().replace(day=1)
        period_label = "This Month"
    else:  # alltime
        start_date = None
        period_label = "All Time"
    
    # Get all users with their study time
    users_query = User.objects.filter(is_active=True)
    
    leaderboard = []
    for user in users_query:
        # Calculate total study minutes for this period
        sessions = StudySession.objects.filter(user=user)
        if start_date:
            sessions = sessions.filter(created_at__date__gte=start_date)
        
        total_minutes = sessions.aggregate(Sum('minutes'))['minutes__sum'] or 0
        total_hours = round(total_minutes / 60, 1)
        
        if total_hours > 0 or period == 'alltime':  # Show users with study time
            leaderboard.append({
                'user': user,
                'total_minutes': total_minutes,
                'total_hours': total_hours,
            })
    
    # Sort by total minutes descending
    leaderboard.sort(key=lambda x: x['total_minutes'], reverse=True)
    
    # Get top 3 for podium
    top_users = leaderboard[:3]
    
    # Find current user's rank
    user_rank = next((i + 1 for i, entry in enumerate(leaderboard) if entry['user'].id == request.user.id), len(leaderboard))
    user_entry = next((entry for entry in leaderboard if entry['user'].id == request.user.id), {'total_hours': 0})
    user_hours = user_entry['total_hours']
    
    # Calculate stats
    top_hours = top_users[0]['total_hours'] if top_users else 0
    hours_to_top = max(0, top_hours - user_hours)
    total_users = len(leaderboard)
    
    # Get recent achievements for current user
    recent_achievements = []
    try:
        user_achievements = Achievement.objects.filter(
            userachievement__user=request.user,
            userachievement__unlocked_at__isnull=False
        ).order_by('-userachievement__unlocked_at')[:3]
        
        for achievement in user_achievements:
            recent_achievements.append({
                'icon': achievement.icon,
                'name': achievement.name,
                'description': achievement.description,
            })
    except:
        # If Achievement model doesn't exist, use placeholder data
        if request.user.profile.total_xp > 100:
            recent_achievements = [
                {'icon': '🎯', 'name': 'First Steps', 'description': 'Completed your first study session'},
                {'icon': '🔥', 'name': 'Week Warrior', 'description': 'Studied for 7 consecutive days'},
            ]
    
    context = {
        'leaderboard': leaderboard,
        'top_users': top_users,
        'user_rank': user_rank,
        'user_hours': user_hours,
        'top_hours': top_hours,
        'hours_to_top': hours_to_top,
        'total_users': total_users,
        'recent_achievements': recent_achievements,
        'period': period,
        'period_label': period_label,
    }
    
    return render(request, 'tracker/leaderboard.html', context)
