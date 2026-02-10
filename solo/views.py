# solo/views.py
"""
Solo Study Room Views
The main study page where magic happens!
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from datetime import timedelta
import json

from tracker.models import Task, StudySession, Achievement, UserAchievement
from accounts.models import UserProfile, UserPreferences


@login_required
def solo_study_room(request):
    """
    Main solo study room page
    This is where users spend most of their time - immersive study experience
    """
    # Get user's profile and preferences
    profile = request.user.profile
    preferences = request.user.preferences
    
    # Get user's active (incomplete) tasks
    active_tasks = Task.objects.filter(user=request.user, completed=False)
    
    # Get today's stats
    today = timezone.now().date()
    today_minutes = StudySession.objects.filter(
        user=request.user,
        created_at__date=today,
        session_type='focus'
    ).aggregate(Sum('minutes'))['minutes__sum'] or 0
    
    # Pack everything into context
    context = {
        'profile': profile,
        'preferences': preferences,
        'user_tasks': active_tasks,
        'today_minutes': today_minutes,
    }
    
    return render(request, 'solo/study_room.html', context)


@login_required
@require_POST
def save_study_session(request):
    """
    Save a completed study session
    Called when timer ends (either focus or break)
    """
    try:
        # Get data from request
        data = json.loads(request.body)
        minutes = int(data.get('minutes', 0))
        session_type = data.get('session_type', 'focus')  # focus or break
        task_id = data.get('task_id', None)  # optional
        completed = data.get('completed', True)  # False if stopped early
        
        # Validate minutes (at least 1 minute to save)
        if minutes < 1:
            return JsonResponse({'success': False, 'error': 'Session too short'}, status=400)
        
        # Create the session
        session = StudySession.objects.create(
            user=request.user,
            minutes=minutes,
            session_type=session_type,
            completed=completed,
            started_at=timezone.now() - timedelta(minutes=minutes),
            ended_at=timezone.now()
        )
        
        # Link to task if provided
        if task_id:
            try:
                task = Task.objects.get(id=task_id, user=request.user)
                session.task = task
                session.save()
            except Task.DoesNotExist:
                pass
        
        # Update profile stats (only for focus sessions)
        if session_type == 'focus':
            profile = request.user.profile
            leveled_up = profile.update_study_stats(minutes)
            
            # Check for achievements
            new_achievements = check_achievements(request.user)
            
            return JsonResponse({
                'success': True,
                'total_minutes': profile.total_study_minutes,
                'current_streak': profile.study_streak,
                'level': profile.level,
                'xp': profile.total_xp,
                'leveled_up': leveled_up,
                'new_achievements': [
                    {'name': a.achievement.name, 'icon': a.achievement.icon}
                    for a in new_achievements
                ]
            })
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def save_auto_session(request):
    """
    Save auto-tracked study session from solo room or group room
    Called automatically when user leaves the room or periodically
    Uses sendBeacon API for reliable delivery
    Note: No @login_required — sendBeacon can't follow redirects.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    try:
        # Get data from request body
        data = json.loads(request.body)
        minutes = int(data.get('minutes', 0))
        session_type = data.get('session_type','focus')
        completed = data.get('completed', True)
        room_code = data.get('room_code', None)  # Optional room code for group study
        
        # Validate minutes (at least 1 minute to save)
        if minutes < 1:
            return JsonResponse({'success': True, 'message': 'Session too short to save'})
        
        # Get room if room_code provided
        room = None
        if room_code:
            try:
                from rooms.models import Room
                room = Room.objects.get(room_code=room_code)
            except Room.DoesNotExist:
                pass
        
        # Create the session
        session = StudySession.objects.create(
            user=request.user,
            minutes=minutes,
            session_type=session_type,
            completed=completed,
            room=room,  # Link to room if provided
            started_at=timezone.now() - timedelta(minutes=minutes),
            ended_at=timezone.now()
        )
        
        # Update profile stats (only for focus sessions)
        if session_type == 'focus':
            profile = request.user.profile
            profile.update_study_stats(minutes)
            
            return JsonResponse({
                'success': True,
                'total_minutes': profile.total_study_minutes,
                'message': f'Saved {minutes} minutes to your profile'
            })
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        # Handle sendBeacon data format
        try:
            # Try to parse as form data
            minutes = int(request.POST.get('minutes', 0))
            if minutes < 1:
                return JsonResponse({'success': True})
            
            session = StudySession.objects.create(
                user=request.user,
                minutes=minutes,
                session_type='focus',
                completed=True,
                started_at=timezone.now() - timedelta(minutes=minutes),
                ended_at=timezone.now()
            )
            
            profile = request.user.profile
            profile.update_study_stats(minutes)
            
            return JsonResponse({'success': True})
        except Exception as inner_e:
            return JsonResponse({'success': False, 'error': str(inner_e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def update_preferences(request):
    """
    Update user preferences (theme, background, sounds, etc.)
    Called when user changes any setting
    """
    try:
        data = json.loads(request.body)
        preferences = request.user.preferences
        
        # Update any provided fields
        if 'theme' in data:
            preferences.theme = data['theme']
        if 'background' in data:
            preferences.background = data['background']
        if 'ambient_sound' in data:
            preferences.ambient_sound = data['ambient_sound']
        if 'sound_volume' in data:
            preferences.sound_volume = int(data['sound_volume'])
        if 'default_focus_duration' in data:
            preferences.default_focus_duration = int(data['default_focus_duration'])
        if 'default_break_duration' in data:
            preferences.default_break_duration = int(data['default_break_duration'])
        if 'auto_start_breaks' in data:
            preferences.auto_start_breaks = data['auto_start_breaks']
        if 'auto_start_focus' in data:
            preferences.auto_start_focus = data['auto_start_focus']
        if 'show_goals_panel' in data:
            preferences.show_goals_panel = data['show_goals_panel']
        
        preferences.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def check_achievements(user):
    """
    Check if user unlocked any new achievements
    Returns list of newly unlocked achievements
    """
    profile = user.profile
    new_achievements = []
    
    # Get all achievements
    all_achievements = Achievement.objects.all()
    
    for achievement in all_achievements:
        # Check if already unlocked
        if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            continue
        
        # Check criteria
        unlocked = False
        
        if achievement.criteria_type == 'first_session':
            if StudySession.objects.filter(user=user).exists():
                unlocked = True
        
        elif achievement.criteria_type == 'total_minutes':
            if profile.total_study_minutes >= achievement.criteria_value:
                unlocked = True
        
        elif achievement.criteria_type == 'streak_days':
            if profile.study_streak >= achievement.criteria_value:
                unlocked = True
        
        elif achievement.criteria_type == 'total_sessions':
            session_count = StudySession.objects.filter(user=user, session_type='focus').count()
            if session_count >= achievement.criteria_value:
                unlocked = True
        
        elif achievement.criteria_type == 'level_reached':
            if profile.level >= achievement.criteria_value:
                unlocked = True
        
        elif achievement.criteria_type == 'deep_focus':
            deep_session = StudySession.objects.filter(
                user=user, 
                minutes__gte=achievement.criteria_value
            ).exists()
            if deep_session:
                unlocked = True
        
        # Unlock achievement
        if unlocked:
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )
            # Award XP bonus
            profile.add_xp(achievement.xp_reward)
            profile.save()
            new_achievements.append(user_achievement)
    
    return new_achievements


@login_required
def get_study_stats(request):
    """
    API endpoint to get study statistics for the Study Stats panel
    Supports filtering by period: today, week, month
    """
    period = request.GET.get('period', 'month')
    user = request.user
    now = timezone.now()
    
    # Determine date range based on period
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = 'Today'
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())  # Start of week (Monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = 'This week'
    else:  # month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = 'This month'
    
    # Get study sessions in the period (only focus sessions)
    sessions = StudySession.objects.filter(
        user=user,
        created_at__gte=start_date,
        session_type='focus',
        completed=True
    )
    
    # Calculate total study time in minutes
    total_minutes = sessions.aggregate(Sum('minutes'))['minutes__sum'] or 0
    study_hours = round(total_minutes / 60, 1)
    
    # Calculate level based on hours
    level_name = 'Beginner (0-3h)'
    next_level = 'Intermediate (3-6h)'
    progress_percentage = min(100, (study_hours / 3) * 100)
    hours_left = max(0, 3 - study_hours)
    
    if study_hours >= 10:
        level_name = 'Expert (10h+)'
        next_level = 'Master'
        progress_percentage = 100
        hours_left = 0
    elif study_hours >= 6:
        level_name = 'Proficient (6-10h)'
        next_level = 'Expert (10h+)'
        progress_percentage = ((study_hours - 6) / 4) * 100
        hours_left = round(10 - study_hours, 1)
    elif study_hours >= 3:
        level_name = 'Intermediate (3-6h)'
        next_level = 'Proficient (6-10h)'
        progress_percentage = ((study_hours - 3) / 3) * 100
        hours_left = round(6 - study_hours, 1)
    
    # Get goals data
    total_goals = Task.objects.filter(user=user).count()
    open_goals = Task.objects.filter(user=user, completed=False).count()
    completed_goals = Task.objects.filter(user=user, completed=True).count()
    
    # Get leaderboard rank (based on total study time)
    user_total_minutes = StudySession.objects.filter(
        user=user,
        session_type='focus',
        completed=True
    ).aggregate(Sum('minutes'))['minutes__sum'] or 0
    
    # Count users with more study time
    from django.contrib.auth.models import User
    from django.db.models import Q
    
    users_with_more_time = User.objects.filter(
        study_sessions__session_type='focus',
        study_sessions__completed=True
    ).annotate(
        total_time=Sum('study_sessions__minutes')
    ).filter(
        total_time__gt=user_total_minutes
    ).distinct().count()
    
    rank = users_with_more_time + 1
    
    # Get recent sessions (last 5 sessions in the period)
    recent_sessions = sessions.order_by('-created_at')[:5].values(
        'minutes',
        'created_at',
        'completed'
    )
    
    # Format recent sessions for JSON
    recent_sessions_list = []
    for session in recent_sessions:
        # Format the date/time
        session_date = session['created_at']
        if timezone.now().date() == session_date.date():
            time_str = session_date.strftime('%I:%M %p')
        else:
            time_str = session_date.strftime('%b %d, %I:%M %p')
        
        recent_sessions_list.append({
            'minutes': session['minutes'],
            'time': time_str,
            'completed': session['completed']
        })
    
    return JsonResponse({
        'success': True,
        'period': period_label,
        'study_hours': study_hours,
        'total_minutes': total_minutes,
        'level_name': level_name,
        'next_level': next_level,
        'progress_percentage': round(progress_percentage, 1),
        'hours_left': hours_left,
        'open_goals': open_goals,
        'completed_goals': completed_goals,
        'total_goals': total_goals,
        'rank': rank,
        'recent_sessions': recent_sessions_list,
    })
