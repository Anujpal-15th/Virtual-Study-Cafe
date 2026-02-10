# VirtualCafe Project Flowcharts

This document contains comprehensive flowcharts for the VirtualCafe online study platform.

---

## Table of Contents
1. [Authentication Flow](#1-authentication-flow)
2. [Main Application Flow](#2-main-application-flow)
3. [Study Room Flow](#3-study-room-flow)
4. [Solo Study Session Flow](#4-solo-study-session-flow)
5. [Progress Tracking Flow](#5-progress-tracking-flow)
6. [Room Management Flow](#6-room-management-flow)
7. [Chatbot Interaction Flow](#7-chatbot-interaction-flow)
8. [Overall System Architecture](#8-overall-system-architecture)

---

## 1. Authentication Flow

### Sign Up & Email Verification

```mermaid
flowchart TD
    Start([User Visits Site]) --> CheckAuth{User Logged In?}
    CheckAuth -->|Yes| Dashboard[Redirect to Dashboard]
    CheckAuth -->|No| Landing[Show Landing Page]
    
    Landing --> ClickSignup[Click Sign Up]
    ClickSignup --> SignupForm[Display Signup Form]
    
    SignupForm --> FillForm[User Enters:<br/>- Username<br/>- Email<br/>- Gender<br/>- Password]
    FillForm --> SubmitForm[Submit Form]
    
    SubmitForm --> ValidateForm{Form Valid?}
    ValidateForm -->|No| ShowErrors[Show Validation Errors]
    ShowErrors --> SignupForm
    
    ValidateForm -->|Yes| CreateUser[Create User Account]
    CreateUser --> CreateProfile[Auto-create UserProfile<br/>via Django Signal]
    CreateProfile --> CreatePrefs[Auto-create UserPreferences<br/>via Django Signal]
    CreatePrefs --> GenToken[Generate UUID Token]
    GenToken --> CreateVerification[Create EmailVerification<br/>Record expires in 24h]
    CreateVerification --> SendEmail[Send Verification Email<br/>with Token Link]
    SendEmail --> ShowSuccess[Show 'Check Email' Message]
    ShowSuccess --> WaitVerify[Wait for User to Click Link]
    
    WaitVerify --> ClickLink[User Clicks Verification Link]
    ClickLink --> VerifyToken{Token Valid &<br/>Not Expired?}
    VerifyToken -->|No| ShowError[Show 'Invalid/Expired Token']
    ShowError --> ResendOption[Offer Resend Option]
    ResendOption --> GenToken
    
    VerifyToken -->|Yes| MarkVerified[Set email_verified = True<br/>in UserProfile]
    MarkVerified --> DeleteToken[Delete EmailVerification Record]
    DeleteToken --> VerifySuccess[Show Success Message]
    VerifySuccess --> RedirectLogin[Redirect to Login]
```

### Login Flow

```mermaid
flowchart TD
    Start([User Goes to Login]) --> LoginForm[Display Login Form]
    LoginForm --> EnterCreds[User Enters:<br/>- Username<br/>- Password]
    EnterCreds --> Submit[Submit Form]
    
    Submit --> Authenticate{Credentials<br/>Valid?}
    Authenticate -->|No| ShowError[Show 'Invalid Credentials']
    ShowError --> LoginForm
    
    Authenticate -->|Yes| LoginUser[Create Session<br/>via Django login]
    LoginUser --> CheckVerified{Email<br/>Verified?}
    
    CheckVerified -->|No| Warning[Show Warning Message:<br/>'Please verify email']
    Warning --> AllowAccess[Allow Access Anyway]
    
    CheckVerified -->|Yes| Success[Login Success]
    AllowAccess --> RedirectHome[Redirect to Dashboard]
    Success --> RedirectHome
    
    RedirectHome --> Dashboard[User Dashboard<br/>with Rooms & Stats]
```

### Password Reset Flow

```mermaid
flowchart TD
    Start([Forgot Password]) --> ResetForm[Display Password Reset Form]
    ResetForm --> EnterEmail[User Enters Email]
    EnterEmail --> Submit[Submit]
    
    Submit --> CheckEmail{Email<br/>Exists?}
    CheckEmail -->|No| ShowSuccess[Show Success Message<br/>regardless for security]
    CheckEmail -->|Yes| GenResetToken[Generate Reset Token<br/>via Django]
    GenResetToken --> SendResetEmail[Send Reset Email<br/>with Token Link]
    SendResetEmail --> ShowSuccess
    
    ShowSuccess --> ClickResetLink[User Clicks Reset Link]
    ClickResetLink --> ValidateToken{Token Valid?}
    ValidateToken -->|No| ExpiredMsg[Show 'Expired Link']
    ValidateToken -->|Yes| NewPasswordForm[Show New Password Form]
    
    NewPasswordForm --> EnterNewPass[User Enters New Password]
    EnterNewPass --> SubmitNew[Submit]
    SubmitNew --> UpdatePass[Update User Password]
    UpdatePass --> ResetSuccess[Show Success Message]
    ResetSuccess --> RedirectLogin[Redirect to Login]
```

---

## 2. Main Application Flow

```mermaid
flowchart TD
    Start([User Logs In]) --> Dashboard[Dashboard Home Page]
    
    Dashboard --> Choice{User Wants To?}
    
    Choice -->|Join/Create Room| RoomSection[Study Rooms Section]
    Choice -->|Solo Study| SoloStudy[Solo Study Room]
    Choice -->|View Progress| ProgressPage[Progress & Stats]
    Choice -->|Ask AI Tutor| Chatbot[AI Chatbot]
    Choice -->|Edit Profile| Profile[Profile Settings]
    Choice -->|View Notifications| Notifications[Notifications Page]
    Choice -->|Logout| LogoutAction[Logout & Clear Session]
    
    RoomSection --> RoomFlow[See Room Management Flow]
    SoloStudy --> SoloFlow[See Solo Study Flow]
    ProgressPage --> ProgressFlow[See Progress Tracking Flow]
    Chatbot --> ChatFlow[See Chatbot Flow]
    Profile --> EditProfile[Edit Avatar, Bio, Gender, Timezone]
    Notifications --> ViewNotifs[View System Notifications]
    LogoutAction --> Landing[Return to Landing Page]
```

---

## 3. Study Room Flow

```mermaid
flowchart TD
    Start([User Enters Rooms Section]) --> ViewRooms[Display Available Rooms]
    ViewRooms --> SearchFilter{User Actions?}
    
    SearchFilter -->|Search| ApplySearch[Filter Rooms by<br/>Name/Description]
    ApplySearch --> ViewRooms
    
    SearchFilter -->|Create New Room| CreateForm[Show Room Creation Form]
    CreateForm --> EnterDetails[User Enters:<br/>- Room Name<br/>- Description<br/>- Max Members<br/>- Public/Private]
    EnterDetails --> SubmitCreate[Submit Form]
    SubmitCreate --> ValidateRoom{Valid?}
    ValidateRoom -->|No| ShowErrors[Show Errors]
    ShowErrors --> CreateForm
    ValidateRoom -->|Yes| CreateRoom[Create Room in DB]
    CreateRoom --> CreateMembership[Auto-add Creator as Member]
    CreateMembership --> SetExpiry[Set Expiry Timer<br/>if temp room]
    SetExpiry --> RedirectRoom[Redirect to Room Detail]
    
    SearchFilter -->|Join Existing Room| SelectRoom[Click on Room]
    SelectRoom --> CheckCapacity{Room<br/>Full?}
    CheckCapacity -->|Yes| ShowFull[Show 'Room Full' Message]
    CheckCapacity -->|No| JoinRoom[Create RoomMembership]
    JoinRoom --> RedirectRoom
    
    RedirectRoom --> RoomDetail[Room Detail Page]
    RoomDetail --> RoomFeatures{User Actions in Room?}
    
    RoomFeatures -->|Chat| WebSocketChat[Real-time Chat<br/>via Django Channels]
    RoomFeatures -->|Video Call| WebRTC[P2P Video Call<br/>via WebRTC]
    RoomFeatures -->|Study Timer| StartTimer[Start Study Session]
    RoomFeatures -->|View Members| ListMembers[Show Active Members]
    RoomFeatures -->|Leave Room| LeaveAction[Set is_active = False]
    
    StartTimer --> SaveSession[Log Study Session<br/>to Tracker]
    SaveSession --> UpdateStats[Update User XP & Stats]
    
    LeaveAction --> CheckEmpty{Room<br/>Empty?}
    CheckEmpty -->|Yes| StartExpiry[Start 30-min Expiry Timer]
    CheckEmpty -->|No| ReturnDash[Return to Dashboard]
    StartExpiry --> ReturnDash
```

---

## 4. Solo Study Session Flow

```mermaid
flowchart TD
    Start([User Opens Solo Study Room]) --> LoadRoom[Load Study Room Page]
    LoadRoom --> DisplayUI[Display:<br/>- Pomodoro Timer<br/>- Task List<br/>- Background Options<br/>- Ambient Sound]
    
    DisplayUI --> UserAction{User Actions?}
    
    UserAction -->|Create Task| TaskForm[Enter Task Name]
    TaskForm --> SaveTask[Create Task in DB]
    SaveTask --> DisplayUI
    
    UserAction -->|Select Task| SelectTask[Mark Task as Active]
    SelectTask --> DisplayUI
    
    UserAction -->|Change Background| ChangeTheme[Update Theme Preference]
    ChangeTheme --> SavePref[Update UserPreferences]
    SavePref --> DisplayUI
    
    UserAction -->|Change Sound| ChangeSound[Update Ambient Sound]
    ChangeSound --> SavePref
    
    UserAction -->|Start Timer| ConfigTimer{Timer Type?}
    
    ConfigTimer -->|Focus Session| SetFocus[Set 25-min Focus Timer]
    ConfigTimer -->|Break Session| SetBreak[Set 5-min Break Timer]
    ConfigTimer -->|Custom| SetCustom[Set Custom Duration]
    
    SetFocus --> StartTimer[Start Countdown]
    SetBreak --> StartTimer
    SetCustom --> StartTimer
    
    StartTimer --> TimerRunning{Timer Status?}
    
    TimerRunning -->|User Stops Early| StopEarly[Stop Timer]
    StopEarly --> CalcMinutes[Calculate Minutes Elapsed]
    CalcMinutes --> SaveSession
    
    TimerRunning -->|Completes| TimerEnds[Timer Reaches 00:00]
    TimerEnds --> PlaySound[Play Completion Sound]
    PlaySound --> GetMinutes[Get Total Minutes]
    GetMinutes --> SaveSession[Create StudySession Record:<br/>- minutes<br/>- session_type focus/break<br/>- task_id if linked<br/>- completed true/false]
    
    SaveSession --> CheckType{Session Type?}
    CheckType -->|Break| SkipXP[Skip XP Update]
    CheckType -->|Focus| UpdateProfile[Update UserProfile Stats:<br/>- total_study_minutes<br/>- XP points<br/>- Level up if threshold]
    
    UpdateProfile --> CheckLevel{Leveled Up?}
    CheckLevel -->|Yes| ShowLevelUp[Show Level Up Animation]
    CheckLevel -->|No| CheckAchieve
    ShowLevelUp --> CheckAchieve{New Achievements?}
    
    SkipXP --> ReturnStats
    CheckAchieve -->|Yes| UnlockAchieve[Create UserAchievement<br/>Show Badge Notification]
    CheckAchieve -->|No| ReturnStats[Return Study Stats JSON]
    UnlockAchieve --> ReturnStats
    
    ReturnStats --> UpdateUI[Update UI with New Stats]
    UpdateUI --> DisplayUI
```

---

## 5. Progress Tracking Flow

```mermaid
flowchart TD
    Start([User Opens Progress Page]) --> LoadData[Query Database]
    LoadData --> GetToday[Get Today's Study Sessions]
    GetToday --> CalcToday[Sum Today's Minutes]
    
    CalcToday --> GetWeek[Get This Week's Sessions<br/>Monday to Today]
    GetWeek --> CalcWeek[Sum Week's Minutes]
    
    CalcWeek --> GetLast7[Get Last 7 Days<br/>Day-by-Day Data]
    GetLast7 --> ProcessDays[For Each Day:<br/>- Calculate Total Minutes<br/>- Convert to Hours<br/>- Calculate Productivity %]
    
    ProcessDays --> GetRecent[Get 10 Most Recent Sessions]
    GetRecent --> GetAchievements[Get User's Achievements<br/>Ordered by Unlock Date]
    
    GetAchievements --> CalcGoal[Calculate Weekly Goal %<br/>Target: 40 hours = 100%]
    CalcGoal --> PrepareCharts[Prepare Chart Data:<br/>- Bar Chart Last 7 Days<br/>- Productivity Line<br/>- Completion Circle]
    
    PrepareCharts --> RenderPage[Render Progress Page]
    RenderPage --> DisplayCharts[Display:<br/>- Today's Total<br/>- Week's Total<br/>- 7-Day Chart<br/>- Recent Sessions List<br/>- Achievement Badges]
    
    DisplayCharts --> UserView{User Actions?}
    UserView -->|View Session Details| ShowDetails[Expand Session Info]
    UserView -->|Filter by Date| ApplyFilter[Reload with Filter]
    UserView -->|Return to Dashboard| BackDash[Redirect to Home]
    
    ShowDetails --> DisplayCharts
    ApplyFilter --> LoadData
```

---

## 6. Room Management Flow

```mermaid
flowchart TD
    Start([System Background Process]) --> Scheduler[APScheduler Running]
    
    Scheduler --> CleanupTask[Periodic Cleanup Task<br/>Runs Every 30 Minutes]
    CleanupTask --> QueryExpired[Query Rooms Where:<br/>expires_at <= NOW]
    
    QueryExpired --> CheckExpired{Any Expired<br/>Rooms?}
    CheckExpired -->|No| Sleep[Wait 30 Minutes]
    CheckExpired -->|Yes| DeleteRooms[Delete Expired Rooms]
    DeleteRooms --> CountDeleted[Count Deleted]
    CountDeleted --> LogEvent[Log Cleanup Event]
    LogEvent --> Sleep
    
    Sleep --> CleanupTask
    
    UserJoin([User Joins Room]) --> CreateMember[Create RoomMembership<br/>is_active = True]
    CreateMember --> UpdateActivity[Update Room.last_activity<br/>to NOW]
    UpdateActivity --> CancelExpiry{Room had<br/>Expiry Set?}
    CancelExpiry -->|Yes| ClearExpiry[Set expires_at = NULL<br/>Room is Active]
    CancelExpiry -->|No| RoomReady
    ClearExpiry --> RoomReady[Room Ready for Use]
    
    UserLeave([User Leaves Room]) --> DeactivateMember[Set RoomMembership<br/>is_active = False]
    DeactivateMember --> CheckMembers{Any Active<br/>Members Left?}
    CheckMembers -->|Yes| UpdateLast[Update last_activity]
    CheckMembers -->|No| RoomEmpty[Room is Empty]
    RoomEmpty --> SetExpiry[Set expires_at =<br/>NOW + 30 minutes]
    SetExpiry --> ScheduleDelete[Schedule for Deletion]
    
    UpdateLast --> RoomActive[Room Remains Active]
```

---

## 7. Chatbot Interaction Flow

```mermaid
flowchart TD
    Start([User Opens Chatbot]) --> LoadUI[Display Chat Interface]
    LoadUI --> UserType[User Types Question]
    UserType --> SubmitMsg[Submit Message]
    
    SubmitMsg --> Validate{Message<br/>Empty?}
    Validate -->|Yes| ShowError[Show 'Enter Message']
    ShowError --> LoadUI
    
    Validate -->|No| CheckAPI{GEMINI_API_KEY<br/>Configured?}
    CheckAPI -->|No| ShowKeyError[Show 'API Not Configured'<br/>Link to Google AI Studio]
    ShowKeyError --> LoadUI
    
    CheckAPI -->|Yes| CheckClient{Gemini Client<br/>Initialized?}
    CheckClient -->|No| ShowInitError[Show 'Initialization Failed']
    ShowInitError --> LoadUI
    
    CheckClient -->|Yes| BuildPrompt[Construct Prompt:<br/>- System Instructions<br/>- User Message]
    BuildPrompt --> CallAPI[Call Gemini API<br/>generate_content]
    
    CallAPI --> APIResult{API Call<br/>Success?}
    APIResult -->|No| ShowAPIError[Show Error Message]
    ShowAPIError --> LoadUI
    
    APIResult -->|Yes| GetResponse[Extract AI Response Text]
    GetResponse --> FormatResponse[Format Response:<br/>- Bold Questions**<br/>- Emoji Bullets<br/>- Line Breaks]
    FormatResponse --> ReturnJSON[Return JSON:<br/>reply: formatted_text]
    ReturnJSON --> DisplayReply[Display AI Reply in Chat]
    
    DisplayReply --> UpdateHistory[Add to Chat History]
    UpdateHistory --> LoadUI
    
    LoadUI --> UserContinue{User Actions?}
    UserContinue -->|Ask Another Question| UserType
    UserContinue -->|Clear Chat| ClearHistory[Clear Chat Log]
    UserContinue -->|Close Chatbot| ClosePage[Return to Dashboard]
    
    ClearHistory --> LoadUI
```

---

## 8. Overall System Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer (Browser)"]
        HTML[HTML Templates<br/>Django Template Engine]
        CSS[CSS Styling<br/>Glassmorphism Design]
        JS[JavaScript<br/>- chat.js<br/>- room.js<br/>- chatbot.js]
    end
    
    subgraph WebServer["Web Server Layer"]
        Django[Django 4.2.7<br/>WSGI Server]
        Channels[Django Channels<br/>ASGI WebSocket Server]
        Static[Static Files Server<br/>CSS, JS, Images]
        Media[Media Files Server<br/>Avatar Uploads]
    end
    
    subgraph AppLayer["Application Layer (6 Django Apps)"]
        direction TB
        Accounts[Accounts App<br/>- Authentication<br/>- Profiles<br/>- Email Verification<br/>- Notifications]
        Rooms[Rooms App<br/>- Room Management<br/>- WebSocket Chat<br/>- Video Calls<br/>- Memberships]
        Solo[Solo App<br/>- Study Room UI<br/>- Pomodoro Timer<br/>- Task Management]
        Tracker[Tracker App<br/>- Study Sessions<br/>- Progress Stats<br/>- Achievements<br/>- Leaderboard]
        Chatbot[Chatbot App<br/>- AI Tutor API<br/>- Gemini Integration]
        Notifications[Notifications App<br/>- User Alerts<br/>- System Messages]
    end
    
    subgraph DataLayer["Data Layer"]
        SQLite[(SQLite Database<br/>- Users<br/>- Rooms<br/>- Sessions<br/>- Tasks<br/>- Achievements)]
        FileSystem[File System<br/>Media: Avatars]
    end
    
    subgraph External["External Services"]
        Gmail[Gmail SMTP<br/>Email Verification]
        GeminiAPI[Google Gemini API<br/>AI Chatbot]
        WebRTC[WebRTC STUN/TURN<br/>Video Calling]
    end
    
    subgraph Background["Background Tasks"]
        Scheduler[APScheduler<br/>Room Cleanup<br/>Every 30 min]
    end
    
    Client <--> WebServer
    WebServer <--> AppLayer
    AppLayer <--> DataLayer
    AppLayer <--> External
    AppLayer <--> Background
    
    Django -.-> Accounts
    Django -.-> Rooms
    Django -.-> Solo
    Django -.-> Tracker
    Django -.-> Chatbot
    Django -.-> Notifications
    
    Channels -.-> Rooms
    
    Accounts <-.-> Gmail
    Chatbot <-.-> GeminiAPI
    Rooms <-.-> WebRTC
    Rooms <-.-> Scheduler
    
    style Client fill:#e1f5ff
    style WebServer fill:#fff4e1
    style AppLayer fill:#e8f5e9
    style DataLayer fill:#f3e5f5
    style External fill:#ffe0e0
    style Background fill:#fff9c4
```

---

## System Flow Summary

### Key User Journeys

1. **New User Journey**
   - Landing Page → Sign Up → Email Verification → Login → Dashboard → Choose Study Mode

2. **Study Session Journey**
   - Dashboard → Solo Study Room → Start Timer → Complete Session → Save Progress → View Stats

3. **Collaborative Study Journey**
   - Dashboard → Browse Rooms → Join/Create Room → Chat & Video → Study Together → Leave Room

4. **Progress Tracking Journey**
   - Dashboard → Progress Page → View Charts → See Achievements → Set Goals

5. **AI Assistance Journey**
   - Any Page → Open Chatbot → Ask Question → Get AI Tutor Response → Continue Studying

### Technology Integrations

- **Django Framework**: Core MVC architecture, ORM, authentication
- **Django Channels**: WebSocket for real-time chat in study rooms
- **WebRTC**: Peer-to-peer video calling between room members
- **Google Gemini AI**: Intelligent tutoring chatbot
- **Gmail SMTP**: Email verification system
- **APScheduler**: Background task for room cleanup
- **SQLite**: Development database (PostgreSQL-ready)

### Security Features

- Email verification before full access
- CSRF protection on all forms
- Environment-based configuration (.env file)
- Password reset with token expiration
- Session management with Django auth
- Input validation on all user data

---

## Database Models Overview

```mermaid
erDiagram
    User ||--o| UserProfile : has
    User ||--o| UserPreferences : has
    User ||--o{ StudySession : creates
    User ||--o{ Task : creates
    User ||--o{ Room : creates
    User ||--o{ RoomMembership : has
    User ||--o{ UserAchievement : earns
    User ||--o| EmailVerification : has
    
    Room ||--o{ RoomMembership : contains
    Room ||--o{ Message : contains
    
    Task ||--o{ StudySession : linked_to
    
    Achievement ||--o{ UserAchievement : unlocked_as
    
    User {
        int id PK
        string username
        string email
        string password
    }
    
    UserProfile {
        int id PK
        int user_id FK
        string avatar
        string gender
        string bio
        int total_study_minutes
        int xp
        int level
        int study_streak
        bool email_verified
    }
    
    UserPreferences {
        int id PK
        int user_id FK
        string theme
        string background
        string ambient_sound
        int focus_duration
    }
    
    Room {
        int id PK
        string name
        string description
        int created_by_id FK
        int max_members
        bool is_public
        datetime expires_at
        datetime last_activity
    }
    
    RoomMembership {
        int id PK
        int room_id FK
        int user_id FK
        bool is_active
        datetime joined_at
    }
    
    StudySession {
        int id PK
        int user_id FK
        int task_id FK
        int minutes
        string session_type
        bool completed
        datetime started_at
        datetime ended_at
    }
    
    Task {
        int id PK
        int user_id FK
        string name
        bool completed
        datetime created_at
    }
    
    Achievement {
        int id PK
        string name
        string description
        string icon
        string category
        int requirement
    }
    
    UserAchievement {
        int id PK
        int user_id FK
        int achievement_id FK
        datetime unlocked_at
    }
    
    EmailVerification {
        int id PK
        int user_id FK
        string token UUID
        datetime created_at
        datetime expires_at
    }
```

---

## File Structure Map

```
VirtualCafe/
├── accounts/          # User authentication & profiles
│   ├── views.py       # signup, login, verify_email, profile
│   ├── models.py      # UserProfile, UserPreferences, EmailVerification
│   ├── forms.py       # SignUpForm, ProfileUpdateForm
│   └── urls.py        # /login, /signup, /verify-email/
│
├── rooms/             # Study room management
│   ├── views.py       # home, create_room, room_detail
│   ├── models.py      # Room, RoomMembership, Message
│   ├── consumers.py   # WebSocket chat handler
│   ├── routing.py     # WebSocket URL routing
│   └── scheduler.py   # APScheduler for cleanup
│
├── solo/              # Solo study mode
│   ├── views.py       # solo_study_room, save_session
│   └── task_views.py  # task CRUD operations
│
├── tracker/           # Progress tracking
│   ├── views.py       # progress, leaderboard, study_goals
│   ├── models.py      # StudySession, Task, Achievement
│   └── management/    # create_achievements command
│
├── chatbot/           # AI tutor
│   ├── views.py       # chatbot_api (Gemini integration)
│   └── urls.py        # /chatbot/
│
├── notifications/     # User notifications
│   └── models.py      # Notification model
│
├── templates/         # HTML templates
│   ├── base.html      # Base template with sidebar
│   ├── accounts/      # login.html, signup.html, profile.html
│   ├── rooms/         # home.html, room_detail.html
│   └── solo/          # study_room.html
│
├── static/            # CSS, JS, Images
│   ├── css/           # style.css, chatbot.css
│   └── js/            # chat.js, room.js, chatbot.js
│
├── virtualcafe/       # Django project settings
│   ├── settings.py    # Configuration (uses .env)
│   ├── urls.py        # Main URL routing
│   └── asgi.py        # ASGI config for Channels
│
├── .env               # Environment variables (secrets)
├── db.sqlite3         # SQLite database
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

---

## API Endpoints Summary

### Accounts App
- `GET /` - Landing page (if not authenticated)
- `GET /signup/` - Sign up form
- `POST /signup/` - Create new user
- `GET /login/` - Login form
- `POST /login/` - Authenticate user
- `GET /logout/` - Log out user
- `GET /verify-email/<uuid>/` - Verify email with token
- `GET /profile/` - View user profile
- `POST /profile/edit/` - Edit profile
- `GET /notifications/` - View notifications

### Rooms App
- `GET /home/` - Dashboard (rooms list)
- `GET /create/` - Create room form
- `POST /create/` - Create new room
- `GET /room/<slug>/` - Room detail page
- `POST /join/` - Join room by code
- `WS /ws/room/<slug>/` - WebSocket for real-time chat

### Solo App
- `GET /study/` - Solo study room
- `POST /study/save-session/` - Save study session
- `POST /study/tasks/` - Create task
- `PUT /study/tasks/<id>/` - Update task
- `DELETE /study/tasks/<id>/` - Delete task

### Tracker App
- `GET /progress/` - Progress page with stats
- `GET /leaderboard/` - User leaderboard
- `GET /goals/` - Study goals page

### Chatbot App
- `POST /chatbot/` - AI tutor API (JSON request/response)

---

## Deployment Flow

```mermaid
flowchart LR
    Dev[Development<br/>SQLite + DEBUG=True] --> Test[Testing<br/>Run test_all_features.py]
    Test --> Config[Configure Production<br/>- Set DEBUG=False<br/>- Update ALLOWED_HOSTS<br/>- Set DATABASE_URL<br/>- Set SECRET_KEY]
    Config --> Migrate[Run Migrations<br/>python manage.py migrate]
    Migrate --> Static[Collect Static Files<br/>collectstatic]
    Static --> Deploy[Deploy to Server<br/>- Gunicorn WSGI<br/>- Daphne ASGI<br/>- Nginx Reverse Proxy]
    Deploy --> Live[Production Live]
```

---

**Document Version:** 1.0  
**Last Updated:** February 10, 2026  
**Project:** VirtualCafe - Online Study Platform
