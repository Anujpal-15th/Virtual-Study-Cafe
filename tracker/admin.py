"""
Admin configuration for tracker app.
"""
from django.contrib import admin
from .models import StudySession, Task, Achievement, UserAchievement, StudySchedule


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """
    Admin interface for StudySession model.
    """
    list_display = ['user', 'session_type', 'minutes', 'completed', 'task', 'room', 'created_at']
    list_filter = ['session_type', 'completed', 'created_at', 'user']
    search_fields = ['user__username', 'room__name', 'task__title']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model.
    """
    list_display = ['title', 'user', 'priority', 'due_date', 'completed', 'created_at']
    list_filter = ['priority', 'completed', 'created_at']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'created_at'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    Admin interface for Achievement model.
    """
    list_display = ['icon', 'name', 'criteria_type', 'criteria_value', 'xp_reward']
    list_filter = ['criteria_type']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """
    Admin interface for UserAchievement model.
    """
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['unlocked_at']
    search_fields = ['user__username', 'achievement__name']
    date_hierarchy = 'unlocked_at'


@admin.register(StudySchedule)
class StudyScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for StudySchedule model.
    """
    list_display = ['user', 'title', 'date', 'start_time', 'end_time', 'category', 'is_completed']
    list_filter = ['category', 'is_completed', 'date']
    search_fields = ['user__username', 'title']
    date_hierarchy = 'date'

