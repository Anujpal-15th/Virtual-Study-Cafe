"""
Auto-cleanup service for inactive rooms.
Removes rooms that are empty and older than 30 minutes.
"""
from django.utils import timezone
from datetime import timedelta
from rooms.models import Room
import logging

logger = logging.getLogger(__name__)


def cleanup_inactive_rooms():
    """
    Remove rooms that are:
    1. Empty (no active members)
    2. Older than 30 minutes from creation or last activity
    
    This function is designed to be run periodically (every 5 minutes recommended)
    """
    try:
        # Calculate the cutoff time (30 minutes ago)
        cutoff_time = timezone.now() - timedelta(minutes=30)
        
        # Find rooms that are old and empty
        old_rooms = Room.objects.filter(
            created_at__lt=cutoff_time  # Created more than 30 minutes ago
        )
        
        rooms_to_delete = []
        
        for room in old_rooms:
            # Check if room is empty (no active members)
            if room.is_empty():
                # Also check last_activity if it exists
                if room.last_activity and room.last_activity < cutoff_time:
                    rooms_to_delete.append(room)
                elif not room.last_activity:
                    # If no last_activity, use created_at
                    rooms_to_delete.append(room)
        
        # Delete the identified rooms
        if rooms_to_delete:
            deleted_count = len(rooms_to_delete)
            room_codes = [room.room_code for room in rooms_to_delete]
            
            for room in rooms_to_delete:
                room.delete()
            
            logger.info(f"Auto-cleanup: Deleted {deleted_count} inactive rooms: {', '.join(room_codes)}")
            return deleted_count
        else:
            logger.debug("Auto-cleanup: No inactive rooms to delete")
            return 0
            
    except Exception as e:
        logger.error(f"Error during room cleanup: {str(e)}")
        return 0


def cleanup_expired_rooms():
    """
    Additional cleanup for rooms with explicit expiration times.
    This removes rooms that have an expires_at time in the past.
    """
    try:
        expired_rooms = Room.objects.filter(
            expires_at__lte=timezone.now(),
            expires_at__isnull=False
        )
        
        deleted_count = expired_rooms.count()
        if deleted_count > 0:
            room_codes = list(expired_rooms.values_list('room_code', flat=True))
            expired_rooms.delete()
            logger.info(f"Expired rooms cleanup: Deleted {deleted_count} rooms: {', '.join(room_codes)}")
            return deleted_count
        return 0
        
    except Exception as e:
        logger.error(f"Error during expired rooms cleanup: {str(e)}")
        return 0


def run_all_cleanup():
    """
    Run all cleanup tasks.
    This is the main function to be scheduled.
    """
    inactive_deleted = cleanup_inactive_rooms()
    expired_deleted = cleanup_expired_rooms()
    
    total_deleted = inactive_deleted + expired_deleted
    
    if total_deleted > 0:
        logger.info(f"Total rooms cleaned up: {total_deleted}")
    
    return total_deleted
