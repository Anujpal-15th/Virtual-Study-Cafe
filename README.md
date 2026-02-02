# ☕ Virtual Cafe - Multi-User Study Rooms Platform

Virtual Cafe is a complete Django web application that provides virtual study rooms where users can collaborate, chat in real-time, have 1-to-1 video calls, use Pomodoro timers, and track their study progress.

## ✨ Features

✅ **User Authentication**
- Sign up / Login / Logout
- Django's built-in authentication system
- Protected routes with login_required decorator

✅ **Study Rooms**
- Create study rooms with unique room codes
- Join multiple rooms
- See active members in each room
- Room descriptions and metadata

✅ **Real-Time Chat**
- WebSocket-based instant messaging
- Join/leave notifications
- Message history
- Clean and intuitive chat interface

✅ **1-to-1 WebRTC Video Calls**
- Peer-to-peer audio/video calling
- Only 2 users can be in video call simultaneously
- Toggle microphone and camera
- Uses Google STUN server for NAT traversal
- WebSocket signaling for connection establishment

✅ **Pomodoro Timer**
- 25/5 and 50/10 minute presets
- Custom timer durations
- Start, pause, and reset controls
- Automatic study session logging on completion

✅ **Progress Tracker**
- Today's total study minutes
- This week's total minutes
- Last 7 days visual chart
- Recent study sessions history

✅ **Admin Panel**
- Manage rooms, memberships, messages, and sessions
- Full Django admin interface

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 4.2.7 |
| **Real-Time** | Django Channels + WebSocket |
| **Message Broker** | Redis |
| **WebRTC** | Native WebRTC API (Peer-to-Peer) |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **Frontend** | HTML5 + CSS3 + Vanilla JavaScript |
| **Authentication** | Django Authentication |
| **Server** | Daphne (ASGI) |

---

## 📁 Project Structure

```
EY - project/
│
├── virtualcafe/              # Main project folder
│   ├── __init__.py
│   ├── settings.py          # Django settings (INSTALLED_APPS, CHANNEL_LAYERS, etc.)
│   ├── urls.py              # Main URL routing
│   ├── asgi.py              # ASGI configuration for WebSocket
│   └── wsgi.py              # WSGI configuration
│
├── accounts/                 # Authentication app
│   ├── views.py             # signup, login, logout views
│   ├── urls.py
│   └── templates/accounts/
│       ├── signup.html
│       └── login.html
│
├── rooms/                    # Study rooms app
│   ├── models.py            # Room, RoomMembership models
│   ├── views.py             # home, create_room, room_detail views
│   ├── urls.py
│   ├── admin.py
│   └── templates/rooms/
│       ├── home.html
│       ├── create_room.html
│       └── room_detail.html
│
├── chat/                     # Real-time chat app
│   ├── models.py            # ChatMessage model
│   ├── consumers.py         # WebSocket consumer (chat, WebRTC signaling)
│   ├── routing.py           # WebSocket URL routing
│   └── admin.py
│
├── tracker/                  # Progress tracking app
│   ├── models.py            # StudySession model
│   ├── views.py             # progress_view, save_session_view
│   ├── urls.py
│   ├── admin.py
│   └── templates/tracker/
│       └── progress.html
│
├── templates/                # Project-level templates
│   └── base.html            # Base template with navbar
│
├── static/                   # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css        # All styling
│   └── js/
│       └── room.js          # WebSocket, WebRTC, timer logic
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Redis server
- pip (Python package manager)

### Step 1: Clone or Navigate to Project

```bash
cd "d:\Progrraming file\EY - project"
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django 4.2.7
- Django Channels 4.0.0
- channels-redis 4.1.0
- daphne 4.0.0
- redis 5.0.1
- psycopg2-binary (for PostgreSQL support)
- Pillow

### Step 4: Install and Start Redis

**Windows:**
1. Download Redis from [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
2. Extract and run `redis-server.exe`

Or use Docker:
```bash
docker run -p 6379:6379 -d redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 5: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all database tables for:
- Django auth (User model)
- Room and RoomMembership
- ChatMessage
- StudySession

### Step 6: Create Superuser (for Admin Panel)

```bash
python manage.py createsuperuser
```

Enter your desired username, email (optional), and password.

### Step 7: Run the Development Server

```bash
python manage.py runserver
```

Or use Daphne (ASGI server):
```bash
daphne -b 0.0.0.0 -p 8000 virtualcafe.asgi:application
```

The server will start at: **http://localhost:8000**

---

## 🎮 Usage Guide

### 1. Create an Account
- Navigate to http://localhost:8000/signup/
- Enter username and password
- Click "Sign Up"

### 2. Login
- Go to http://localhost:8000/login/
- Enter your credentials
- You'll be redirected to the home dashboard

### 3. Create a Study Room
- Click "Create Room" in the navigation
- Enter room name and description
- Click "Create Room"
- You'll get a unique room code (e.g., A1B2C3)

### 4. Join a Room
- Click "Join Room" on any room card
- You'll be automatically added as a member

### 5. Use the Room Features

**Chat:**
- Type messages in the chat input
- Press Enter or click Send
- See real-time messages from other users
- Get notified when users join/leave

**Video Call:**
- Click "Start Call" to initiate a video call
- Grant camera/microphone permissions
- When another user joins, you'll connect automatically
- Toggle mic/camera as needed
- Click "End Call" to disconnect
- **Note:** Only 2 users can be in a video call at once

**Pomodoro Timer:**
- Click a preset (25/5 or 50/10) or enter custom minutes
- Click "Start" to begin countdown
- Click "Pause" to pause
- Click "Reset" to restart
- When timer completes, your study session is automatically saved

### 6. Track Your Progress
- Click "Progress" in navigation
- View today's total study minutes
- See this week's total
- Check the last 7 days chart
- Review recent study sessions

### 7. Admin Panel (Optional)
- Go to http://localhost:8000/admin/
- Login with superuser credentials
- Manage all rooms, memberships, messages, and study sessions

---

## 🧩 How It Works

### WebSocket Flow

1. **Connection:**
   - User opens room page
   - JavaScript creates WebSocket connection to `ws://localhost:8000/ws/rooms/{room_code}/`
   - Server authenticates user and adds them to room group

2. **Chat Messages:**
   - User types message and clicks Send
   - JavaScript sends JSON: `{"type": "chat", "message": "Hello"}`
   - Consumer receives, saves to database, broadcasts to all in room
   - All users receive and display the message

3. **Join/Leave Notifications:**
   - When user connects, server broadcasts: `{"type": "join", "username": "John"}`
   - When user disconnects, server broadcasts: `{"type": "leave", "username": "John"}`

### WebRTC Flow

1. **Initiating Call:**
   - User A clicks "Start Call"
   - Browser requests camera/microphone access
   - Creates RTCPeerConnection
   - Generates SDP offer
   - Sends offer via WebSocket: `{"type": "webrtc_offer", "offer": {...}}`

2. **Receiving Call:**
   - User B receives offer via WebSocket
   - Creates RTCPeerConnection
   - Sets remote description (offer)
   - Generates SDP answer
   - Sends answer via WebSocket: `{"type": "webrtc_answer", "answer": {...}}`

3. **ICE Candidates:**
   - Both peers exchange ICE candidates via WebSocket
   - `{"type": "webrtc_ice", "candidate": {...}}`
   - Establishes peer-to-peer connection

4. **Connected:**
   - Video streams flow directly between peers (not through server)
   - Audio/video tracks displayed in video elements

### Timer & Session Tracking

1. User starts Pomodoro timer
2. Timer counts down in JavaScript
3. On completion:
   - Alert shown to user
   - POST request sent to `/save-session/`
   - StudySession created in database with minutes
   - User can view stats on `/progress/` page

---

## 🔑 Key Django Concepts Explained

### Models (Database Tables)

**Room:** Stores study room information
- Auto-generates unique 6-character room code
- Tracks creator and creation time

**RoomMembership:** Tracks who's in which room
- `is_active` field shows if user is currently online in room
- Ensures one membership per user per room (unique_together)

**ChatMessage:** Stores chat history
- Links to Room and User
- Ordered by timestamp (oldest first)

**StudySession:** Records completed study sessions
- Stores duration in minutes
- Optional link to Room (can be standalone)

### Views (Request Handlers)

**Function-based views:** Simple Python functions
- `signup_view`: Handles user registration
- `login_view`: Authenticates and logs in user
- `home_view`: Shows all rooms
- `create_room_view`: Creates new room
- `room_detail_view`: Main room interface
- `progress_view`: Shows study statistics

All views use `@login_required` decorator to protect routes.

### WebSocket Consumer

**RoomConsumer:** Handles real-time communication
- Async consumer for better performance
- `connect()`: Join room group
- `receive()`: Handle incoming messages
- Route messages by type (chat, webrtc_offer, etc.)
- `disconnect()`: Leave room group

Uses Django Channels and Redis for message passing between server instances.

---

## 📊 Database Schema

```
User (Django built-in)
  └─ created_rooms (FK to Room)
  └─ room_memberships (FK to RoomMembership)
  └─ messages (FK to ChatMessage)
  └─ study_sessions (FK to StudySession)

Room
  ├─ id (PK)
  ├─ name
  ├─ description
  ├─ room_code (unique)
  ├─ created_by (FK User)
  ├─ created_at
  └─ memberships (reverse FK)

RoomMembership
  ├─ id (PK)
  ├─ user (FK User)
  ├─ room (FK Room)
  ├─ joined_at
  └─ is_active

ChatMessage
  ├─ id (PK)
  ├─ room (FK Room)
  ├─ user (FK User)
  ├─ message
  └─ timestamp

StudySession
  ├─ id (PK)
  ├─ user (FK User)
  ├─ room (FK Room, nullable)
  ├─ minutes
  ├─ started_at
  ├─ ended_at
  └─ created_at
```

---

## 🎨 Frontend Architecture

### HTML Templates

**base.html:** Master template
- Navigation bar with user info
- Message display area
- Footer
- All pages extend this

**Specific Pages:**
- `signup.html` / `login.html`: Authentication forms
- `home.html`: Room listing grid
- `create_room.html`: Room creation form
- `room_detail.html`: Main room interface (chat + video + timer)
- `progress.html`: Statistics and charts

### CSS (style.css)

- Clean, modern design with gradient backgrounds
- Responsive grid layouts
- Card-based UI components
- Hover effects and transitions
- Mobile-responsive (@media queries)

### JavaScript (room.js)

**WebSocket Management:**
- `initWebSocket()`: Connect to room
- `handleWebSocketMessage()`: Route incoming messages
- `sendChatMessage()`: Send chat to server

**WebRTC Functions:**
- `startCall()`: Initialize video call
- `handleWebRTCOffer()`: Respond to call
- `endCall()`: Disconnect
- `toggleMic()` / `toggleCamera()`: Control media

**Timer Functions:**
- `startTimer()`: Begin countdown
- `pauseTimer()`: Pause countdown
- `completeTimer()`: Save session on completion
- `saveStudySession()`: POST to Django endpoint

---

## 🔐 Security Considerations

### Implemented:

✅ CSRF protection on all forms
✅ User authentication required for all main pages
✅ WebSocket authentication via AuthMiddlewareStack
✅ XSS prevention through Django template escaping
✅ Password validation and hashing

### For Production:

⚠️ Change `SECRET_KEY` in settings.py
⚠️ Set `DEBUG = False`
⚠️ Configure `ALLOWED_HOSTS`
⚠️ Use HTTPS (wss:// for WebSocket)
⚠️ Set up proper CORS headers
⚠️ Use environment variables for secrets
⚠️ Add rate limiting for WebSocket connections
⚠️ Implement TURN server for WebRTC behind NAT

---

## 🐛 Troubleshooting

### Redis Connection Error
**Problem:** `Connection refused` when starting server

**Solution:**
```bash
# Windows: Make sure redis-server.exe is running
# macOS/Linux:
redis-cli ping
# Should return: PONG

# If not running:
redis-server
```

### WebSocket Connection Failed
**Problem:** Chat not working, "WebSocket disconnected"

**Solution:**
1. Check Redis is running
2. Verify ASGI application is configured correctly
3. Check browser console for errors
4. Make sure you're using `ws://` (not `wss://`) in development

### Video Call Not Connecting
**Problem:** Camera works but no connection to peer

**Possible Causes:**
1. Firewall blocking WebRTC traffic
2. Need TURN server (not just STUN) for restrictive networks
3. Only 2 users maximum - third user will fail
4. Browser permissions denied

**Solution:**
- Check browser console for errors
- Grant camera/microphone permissions
- Test on same local network first
- For production, set up a TURN server

### Migrations Error
**Problem:** `No such table` errors

**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
**Problem:** CSS/JS not appearing

**Solution:**
```bash
# Make sure STATIC_URL is set in settings.py
# Check that static files are in correct folders:
# static/css/style.css
# static/js/room.js

# For production, run:
python manage.py collectstatic
```

---

## 🚀 Production Deployment

### 1. Update Settings

```python
# settings.py

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'virtualcafe',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Use environment variables for secrets
SECRET_KEY = os.environ.get('SECRET_KEY')

# Redis URL
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}
```

### 2. Collect Static Files

```bash
python manage.py collectstatic
```

### 3. Use Production Server

**Option A: Daphne + Nginx**
```bash
daphne -b 0.0.0.0 -p 8000 virtualcafe.asgi:application
```

**Option B: Gunicorn + Uvicorn Workers**
```bash
pip install gunicorn uvicorn
gunicorn virtualcafe.asgi:application -k uvicorn.workers.UvicornWorker
```

### 4. Set Up Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

### 5. Use Supervisor/Systemd

Keep Daphne running with a process manager.

---

## 📚 Learning Resources

**Django:**
- Official Docs: https://docs.djangoproject.com/
- Django Girls Tutorial: https://tutorial.djangogirls.org/

**Django Channels:**
- Official Docs: https://channels.readthedocs.io/
- Real-time Django: https://realpython.com/getting-started-with-django-channels/

**WebRTC:**
- MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- WebRTC for Beginners: https://webrtc.org/getting-started/overview

**Redis:**
- Official Docs: https://redis.io/docs/

---

## 🤝 Contributing

This is a beginner-friendly educational project. Feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Optimize code

---

## 📄 License

This project is created for educational purposes. Feel free to use and modify as needed.

---

## 🙏 Credits

Developed as a comprehensive Django learning project covering:
- Authentication
- Real-time WebSocket communication
- WebRTC peer-to-peer video
- Database relationships
- Frontend integration
- Async programming with Channels

Perfect for beginners learning full-stack web development with Django!

---

## 📞 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Review browser console for JavaScript errors
3. Check Django server logs for backend errors
4. Ensure Redis is running
5. Verify all migrations are applied

---

**Happy Studying! ☕📚**
#   V i r t u a l C a f e - - - A - o n l i n e - s t u d y - a n d - c o m m u n i c a t i o n  
 