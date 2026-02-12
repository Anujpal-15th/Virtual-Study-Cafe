# Virtual Study Cafe – Online Study Platform

Virtual Cafe is a Django-based online study platform designed to support both collaborative and solo study sessions. It provides real-time communication, structured study tracking, and AI-assisted learning to help students stay focused and accountable.

---

## Features

### Study Rooms
- Create and join public or private study rooms
- Real-time chat using WebSockets
- Browse active study rooms
- Automatic cleanup of inactive rooms
- Discover and connect with other students

### Solo Study
- Dedicated personal study space
- Study timer for tracking focused sessions
- Task management for organizing study work

### AI Assistant
- AI-powered chatbot for study-related questions
- Interactive, real-time chat interface
- Integrated using Google Generative AI (Gemini)

### Progress Tracking
- Track study sessions and total study time
- Leaderboard to compare progress
- Personal study goals
- Achievement system based on milestones

### User Management
- User profiles with avatar support
- Email verification
- Authentication flow (signup, login, password reset)
- Real-time notifications for study activity

---

## Technology Stack

- Backend: Django 4.2.7
- Real-time Communication: Django Channels and WebSockets
- Channel Layer: Redis with channels-redis
- ASGI Server: Daphne
- AI Integration: Google Generative AI (Gemini)
- Task Scheduling: APScheduler
- Image Processing: Pillow
- Database: SQLite (development)

---

## Prerequisites

- Python 3.8 or higher
- Redis server
- pip (Python package manager)

---

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd "EY - project"
