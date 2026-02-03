# Room Expiration Feature

## Overview
Rooms automatically expire after 15 minutes of inactivity when they are empty (no active members).

## How It Works

### Automatic Expiration
- When all members leave a room, a 15-minute expiration timer starts
- If someone joins before the timer expires, the expiration is cancelled
- Once the timer expires, the room is automatically deleted

### Activity Tracking
- `last_activity`: Timestamp of the last room activity
- `expires_at`: Timestamp when the room will expire (set when room becomes empty)

### Automatic Cleanup
The system automatically removes expired rooms in two ways:

1. **On Page Load**: When users visit the dashboard, expired rooms are cleaned up
2. **Manual Command**: Run the cleanup command manually:
   ```bash
   python manage.py cleanup_expired_rooms
   ```

### Signals
The system uses Django signals to automatically update room expiration:
- When a user joins a room → expiration is cleared
- When a user leaves a room → expiration timer starts if room becomes empty

## Technical Details

### New Model Fields (Room)
- `last_activity`: DateTimeField - tracks last activity timestamp
- `expires_at`: DateTimeField - when room will expire if empty (null if room has members)

### New Methods (Room Model)
- `is_empty()`: Returns True if room has no active members
- `is_expired()`: Returns True if room expiration time has passed
- `update_activity()`: Updates activity timestamp and manages expiration

### Management Command
Location: `rooms/management/commands/cleanup_expired_rooms.py`

Run manually:
```bash
python manage.py cleanup_expired_rooms
```

Or set up as a cron job for automatic cleanup:
```bash
# Run every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py cleanup_expired_rooms
```

## User Experience

### Room Creator
- Creates a room and joins it
- Room won't expire as long as at least one person is in it
- If everyone leaves, room will expire in 15 minutes

### Room Member
- Joins an existing room
- Activity timestamp updates
- If trying to join an expired room, redirected with error message

### Dashboard
- Only shows active rooms (non-expired)
- Displays message when expired rooms are removed
- Room codes remain valid until expiration
