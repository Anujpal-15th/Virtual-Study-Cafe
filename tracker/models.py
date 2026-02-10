"""
Tracker app models.
Defines StudySession model for tracking study time.
"""
from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class StudySession(models.Model):
    """
    Represents a study session completed by a user.
    Can be associated with a room, task, or standalone.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    # Session type: focus or break
    session_type = models.CharField(max_length=10, choices=[
        ('focus', 'Focus Session'),
        ('break', 'Break'),
    ], default='focus')
    
    # Duration
    minutes = models.IntegerField()  # Duration of study session in minutes
    planned_minutes = models.IntegerField(null=True, blank=True)  # What they planned to study
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Completion status
    completed = models.BooleanField(default=True)  # False if stopped early
    
    # Linked task (optional)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    def __str__(self):
        return f"{self.user.username} - {self.minutes} min on {self.created_at.date()}"
    
    class Meta:
        ordering = ['-created_at']  # Newest sessions first


class Task(models.Model):
    """
    A goal or task that the user wants to complete
    Can be linked to study sessions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # Task details
    title = models.CharField(max_length=200, help_text="What do you want to accomplish?")
    notes = models.TextField(blank=True, help_text="Optional details or notes")
    
    # Priority level
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
    ], default='medium')
    
    # Due date (optional)
    due_date = models.DateField(null=True, blank=True, help_text="Optional deadline")
    
    # Status
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Order (for drag and drop sorting)
    order = models.IntegerField(default=0, help_text="Display order")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']  # Order by position, then newest first
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"
    
    def mark_complete(self):
        """Mark task as complete"""
        from django.utils import timezone
        self.completed = True
        self.completed_at = timezone.now()
        self.save()


class Achievement(models.Model):
    """
    Achievements that users can unlock
    Like badges or trophies for completing milestones
    """
    # Achievement details
    name = models.CharField(max_length=100, help_text="Achievement name")
    description = models.TextField(help_text="How to unlock this")
    icon = models.CharField(max_length=50, default='🏆', help_text="Emoji icon")
    
    # Unlock criteria
    criteria_type = models.CharField(max_length=50, choices=[
        ('first_session', 'First Session'),
        ('total_minutes', 'Total Minutes'),
        ('streak_days', 'Streak Days'),
        ('total_sessions', 'Total Sessions'),
        ('level_reached', 'Level Reached'),
        ('deep_focus', 'Deep Focus Session'),
    ])
    criteria_value = models.IntegerField(help_text="Required value to unlock")
    
    # XP reward
    xp_reward = models.IntegerField(default=50, help_text="XP bonus for unlocking")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['criteria_value']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """
    Tracks which achievements a user has unlocked
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')  # Can't unlock same achievement twice
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} unlocked {self.achievement.name}"


class StudySchedule(models.Model):
    """
    Represents a scheduled study event on a specific date/time.
    Users can plan study sessions via the dashboard calendar.
    """
    CATEGORY_CHOICES = [
        ('study', '📚 Study'),
        ('review', '🔄 Review'),
        ('exam', '📝 Exam Prep'),
        ('group', '👥 Group Study'),
        ('break', '☕ Break'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_schedules')
    title = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='study')
    notes = models.TextField(blank=True, default='')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.user.username} - {self.title} on {self.date}"

