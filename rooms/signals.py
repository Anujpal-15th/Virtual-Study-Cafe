"""
Signals for the rooms app.
Handles automatic room expiration updates when members leave.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import RoomMembership


@receiver(post_save, sender=RoomMembership)
def update_room_on_membership_change(sender, instance, created, **kwargs):
    """
    Update room activity when membership is created or updated.
    """
    if instance.room:
        instance.room.update_activity()


@receiver(post_delete, sender=RoomMembership)
def update_room_on_member_leave(sender, instance, **kwargs):
    """
    Update room activity when a member leaves (membership deleted).
    Sets expiration if room becomes empty.
    """
    if instance.room:
        try:
            instance.room.update_activity()
        except Exception:
            # Room might have been deleted
            pass
