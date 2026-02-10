"""
Rooms app models.
Defines Room and RoomMembership models for study rooms.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class Room(models.Model):
    """
    Represents a study room where users can join, chat, and video call.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    room_code = models.CharField(max_length=10, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now)  # Track last activity in room
    expires_at = models.DateTimeField(null=True, blank=True)  # When room will expire if empty
    is_public = models.BooleanField(default=True)  # Whether room is visible in public listing
    
    def save(self, *args, **kwargs):
        
        
        if not self.room_code:
            self.room_code = str(uuid.uuid4())[:6].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.room_code})"
    
    def get_member_count(self):
        """
        Returns the count of active members in this room
        """
        return self.memberships.filter(is_active=True).count()
    
    def is_empty(self):
        """
        Check if room has no active members
        """
        return self.get_member_count() == 0
    
    def is_expired(self):
        """
        Check if room has expired (empty for more than 15 minutes)
        """
        if not self.expires_at:
            return False
        return timezone.now() >= self.expires_at
    
    def update_activity(self):
        """
        Update last activity time and clear expiration if room has members.
        """
        self.last_activity = timezone.now()
        
        if not self.is_empty():
            self.expires_at = None  # Clear expiration when room has members
        else:
            # Set expiration for 15 minutes from now if room is empty
            self.expires_at = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['last_activity', 'expires_at'])
    
    class Meta:
        ordering = ['-created_at']  # Newest rooms first


class RoomMembership(models.Model):
    """
    Tracks which users are members of which rooms.
    Also tracks if a user is currently active in the room.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_memberships')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Whether user is currently in the room
    
    def __str__(self):
        return f"{self.user.username} in {self.room.name}"
    
    class Meta:
        # Each user can only have one membership per room
        unique_together = ['user', 'room']
        ordering = ['-joined_at']

