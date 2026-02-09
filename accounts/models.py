"""
Accounts app models - Extended user profile
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import uuid


class UserProfile(models.Model):
    """
    Extended user profile information
    Each user automatically gets a profile when they sign up
    """
    # Link to Django's built-in User model (one profile per user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile picture - uploaded to media/avatars/
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, 
                               help_text="Profile picture (optional)")
    
    # Gender for personalized avatar
    GENDER_CHOICES = [
        ('male', '👨 Male'),
        ('female', '👩 Female'),
        ('other', '🌟 Other'),
        ('prefer_not_to_say', '🔒 Prefer not to say'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, 
                             default='prefer_not_to_say',
                             help_text="Select your gender for personalized avatar")
    
    # Personal information
    bio = models.TextField(max_length=500, blank=True, 
                          help_text="Tell others about yourself")
    
    # User preferences
    timezone = models.CharField(max_length=50, default='UTC', 
                               help_text="Your timezone for scheduling")
    
    # Study tracking
    total_study_minutes = models.IntegerField(default=0, 
                                             help_text="Total minutes studied across all sessions")
    study_streak = models.IntegerField(default=0, 
                                      help_text="Consecutive days with study sessions")
    longest_streak = models.IntegerField(default=0,
                                        help_text="Best streak ever achieved")
    last_study_date = models.DateField(null=True, blank=True,
                                       help_text="Last date user studied")
    
    # Gamification - makes studying fun!
    total_xp = models.IntegerField(default=0, help_text="Experience points earned")
    level = models.IntegerField(default=1, help_text="User level (starts at 1)")
    
    # Social features
    favorite_rooms = models.ManyToManyField('rooms.Room', blank=True, related_name='favorited_by',
                                           help_text="Rooms this user has favorited")
    
    # Email verification
    email_verified = models.BooleanField(default=False, help_text="Has user verified their email?")
    email_verified_at = models.DateTimeField(null=True, blank=True, help_text="When email was verified")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        """
        Returns the avatar URL if exists, otherwise returns gender-specific default avatar
        """
        if self.avatar:
            return self.avatar.url
        
        # Gender-specific avatar URLs with beautiful illustrations
        gender_avatars = {
            'male': f"https://ui-avatars.com/api/?name={self.user.username}&background=4A90E2&color=fff&size=200&bold=true",
            'female': f"https://ui-avatars.com/api/?name={self.user.username}&background=E91E63&color=fff&size=200&bold=true",
            'other': f"https://ui-avatars.com/api/?name={self.user.username}&background=9C27B0&color=fff&size=200&bold=true",
            'prefer_not_to_say': f"https://ui-avatars.com/api/?name={self.user.username}&background=667eea&color=fff&size=200&bold=true",
        }
        
        return gender_avatars.get(self.gender, gender_avatars['prefer_not_to_say'])
    
    def update_study_stats(self, minutes):
        """
        Update total study minutes and calculate streak
        Call this method whenever a study session is saved
        """
        from datetime import date
        
        self.total_study_minutes += minutes
        
        # Add XP: 1 minute = 1 XP
        self.add_xp(minutes)
        
        # Check if user studied today
        today = date.today()
        if self.last_study_date:
            # Calculate days since last study
            days_diff = (today - self.last_study_date).days
            
            if days_diff == 0:
                # Already studied today, don't change streak
                pass
            elif days_diff == 1:
                # Studied yesterday, increment streak
                self.study_streak += 1
            else:
                # Missed days, reset streak
                self.study_streak = 1
        else:
            # First time studying
            self.study_streak = 1
        
        # Update longest streak if needed
        if self.study_streak > self.longest_streak:
            self.longest_streak = self.study_streak
        
        self.last_study_date = today
        self.save()
    
    def add_xp(self, amount):
        """
        Add XP and check if user levels up
        Returns True if user leveled up, False otherwise
        """
        self.total_xp += amount
        
        # Simple leveling: 100 XP per level
        # Level 1 = 0-99 XP, Level 2 = 100-199 XP, Level 3 = 200-299 XP, etc.
        new_level = (self.total_xp // 100) + 1
        
        if new_level > self.level:
            self.level = new_level
            return True  # User leveled up!
        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created
    This signal ensures every user has a profile
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile whenever the user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


class UserPreferences(models.Model):
    """
    User's customization preferences for the solo study room
    Stores theme, timer settings, sounds, backgrounds - everything the user customizes
    """
    # Link to user (one set of preferences per user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Theme preferences (dark mode or light mode)
    theme = models.CharField(max_length=10, choices=[
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
    ], default='dark', help_text="Light or dark theme")
    
    # Background preferences (what the study room looks like)
    background = models.CharField(max_length=50, default='library', help_text="Study room background")
    # Options: library, cafe, nature, ocean, mountains, space, minimal
    
    # Sound preferences (ambient sounds for focus)
    ambient_sound = models.CharField(max_length=50, default='none', help_text="Background ambient sound")
    # Options: none, rain, cafe, white_noise, fire, ocean_waves, forest
    sound_volume = models.IntegerField(default=50, help_text="Volume level 0-100")
    auto_resume_sound = models.BooleanField(default=False, help_text="Auto-play sound when session starts")
    
    # Timer preferences (default duration settings)
    default_focus_duration = models.IntegerField(default=25, help_text="Default focus session minutes")
    default_break_duration = models.IntegerField(default=5, help_text="Default break minutes")
    auto_start_breaks = models.BooleanField(default=False, help_text="Automatically start break after focus")
    auto_start_focus = models.BooleanField(default=False, help_text="Automatically start focus after break")
    
    # Notification preferences
    sound_notification = models.BooleanField(default=True, help_text="Play sound when timer ends")
    browser_notification = models.BooleanField(default=False, help_text="Show browser notification")
    
    # UI preferences
    show_goals_panel = models.BooleanField(default=True, help_text="Show goals/tasks panel")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Automatically create UserPreferences when a new User is created
    """
    if created:
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """
    Save preferences whenever the user is saved
    """
    if hasattr(instance, 'preferences'):
        instance.preferences.save()


class EmailVerification(models.Model):
    """
    Email verification tokens for new user registrations
    Tokens expire after 24 hours
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def __str__(self):
        return f"Verification for {self.user.username} - {'Verified' if self.verified else 'Pending'}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if verification token has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not expired and not already used)"""
        return not self.verified and not self.is_expired()
    
    @classmethod
    def create_for_user(cls, user):
        """Create a new verification token for a user"""
        return cls.objects.create(user=user)

