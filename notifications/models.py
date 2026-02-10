from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    In-app notification system for user alerts
    Examples: room invites, new messages, study milestones
    """
    
    # Notification types - define what kind of notification this is
    NOTIFICATION_TYPES = (
        ('room_invite', 'Room Invitation'),
        ('new_member', 'New Room Member'),
        ('study_milestone', 'Study Milestone'),
        ('message', 'New Message'),
        ('achievement', 'Achievement Unlocked'),
        ('system', 'System Notification'),
    )
    
    # Who receives this notification
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                                   help_text="User who will receive this notification")
    
    # Who triggered this notification (optional - can be system-generated)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sent_notifications',
                               help_text="User who triggered this notification (optional)")
    
    # Notification content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system',
                                         help_text="Type of notification")
    title = models.CharField(max_length=200, help_text="Notification title")
    message = models.TextField(help_text="Detailed notification message")
    
    # Optional link - where to go when user clicks the notification
    link = models.CharField(max_length=500, blank=True, 
                           help_text="URL to redirect when notification is clicked")
    
    # Notification status
    is_read = models.BooleanField(default=False, help_text="Has user read this notification?")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When notification was read")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']  # Newest first
        indexes = [
            models.Index(fields=['recipient', 'is_read']),  # Fast lookup for unread notifications
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type}: {self.title} for {self.recipient.username}"
    
    def mark_as_read(self):
        """
        Mark this notification as read
        """
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_room_invite(cls, recipient, sender, room):
        """
        Helper method: Create a room invitation notification
        
        Args:
            recipient: User who is being invited
            sender: User who sent the invite
            room: Room object they're invited to
        """
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type='room_invite',
            title=f"{sender.username} invited you to a study room",
            message=f"Join '{room.name}' and start studying together!",
            link=f"/rooms/{room.room_code}/"
        )
    
    @classmethod
    def create_study_milestone(cls, user, minutes):
        """
        Helper method: Create a study milestone notification
        
        Args:
            user: User who reached the milestone
            minutes: Total study minutes reached
        """
        # Define milestones
        milestones = {
            60: "🎉 You've studied for 1 hour!",
            300: "🔥 5 hours of focus! Keep it up!",
            600: "⭐ 10 hours milestone! You're amazing!",
            1200: "🏆 20 hours! You're on fire!",
            3000: "💎 50 hours! Study master!",
        }
        
        if minutes in milestones:
            return cls.objects.create(
                recipient=user,
                notification_type='study_milestone',
                title="Study Milestone Reached!",
                message=milestones[minutes],
                link="/progress/"
            )
        return None
    
    @classmethod
    def create_new_member_notification(cls, room_owner, new_member, room):
        """
        Helper method: Notify room owner when someone joins their room
        
        Args:
            room_owner: Owner of the room
            new_member: User who just joined
            room: Room object
        """
        return cls.objects.create(
            recipient=room_owner,
            sender=new_member,
            notification_type='new_member',
            title=f"{new_member.username} joined your room",
            message=f"{new_member.username} is now studying in '{room.name}'",
            link=f"/rooms/{room.room_code}/"
        )
