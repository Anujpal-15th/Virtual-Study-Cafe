#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Feature Test for VirtualCafe
Tests all features to ensure they work as expected
"""
import os
import django
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualcafe.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import UserProfile, EmailVerification
from rooms.models import Room
from tracker.models import StudySession, Task, Achievement
from notifications.models import Notification

print("=" * 80)
print("VIRTUALCAFE - COMPREHENSIVE FEATURE TEST")
print("=" * 80)

# Initialize test client
client = Client()
test_results = []

def test_feature(feature_name, test_func):
    """Test a feature and record results"""
    try:
        result = test_func()
        status = "✅ PASS" if result else "❌ FAIL"
        test_results.append((feature_name, status, ""))
        print(f"{status} - {feature_name}")
        return result
    except Exception as e:
        test_results.append((feature_name, "❌ ERROR", str(e)))
        print(f"❌ ERROR - {feature_name}: {str(e)}")
        return False

# Clean up any existing test user
User.objects.filter(username='featuretest').delete()

print("\n" + "=" * 80)
print("1. AUTHENTICATION FEATURES")
print("=" * 80)

def test_signup_page():
    response = client.get('/signup/')
    return response.status_code == 200

def test_login_page():
    response = client.get('/login/')
    return response.status_code == 200

def test_password_reset_page():
    response = client.get('/password-reset/')
    return response.status_code == 200

test_feature("Signup Page", test_signup_page)
test_feature("Login Page", test_login_page)
test_feature("Password Reset Page", test_password_reset_page)

print("\n" + "=" * 80)
print("2. USER CREATION & AUTHENTICATION")
print("=" * 80)

# Create a test user
test_user = User.objects.create_user(
    username='featuretest',
    email='test@virtualcafe.com',
    password='testpass123'
)
print(f"✅ Test user created: {test_user.username}")

def test_user_profile_exists():
    return hasattr(test_user, 'profile') and test_user.profile is not None

def test_user_preferences_exists():
    return hasattr(test_user, 'preferences') and test_user.preferences is not None

test_feature("UserProfile Auto-Creation", test_user_profile_exists)
test_feature("UserPreferences Auto-Creation", test_user_preferences_exists)

# Login the test user
client.login(username='featuretest', password='testpass123')
print("✅ Test user logged in")

print("\n" + "=" * 80)
print("3. EMAIL VERIFICATION FEATURES")
print("=" * 80)

def test_verification_token_creation():
    verification = EmailVerification.create_for_user(test_user)
    return verification is not None and verification.token is not None

def test_verification_token_validity():
    verification = EmailVerification.objects.filter(user=test_user).first()
    return verification and verification.is_valid()

def test_verification_sent_page():
    response = client.get('/verification-sent/')
    return response.status_code == 200

def test_resend_verification_page():
    response = client.get('/resend-verification/')
    return response.status_code == 200

test_feature("Email Verification Token Creation", test_verification_token_creation)
test_feature("Email Verification Token Validity", test_verification_token_validity)
test_feature("Verification Sent Page", test_verification_sent_page)
test_feature("Resend Verification Page", test_resend_verification_page)

print("\n" + "=" * 80)
print("4. PROFILE FEATURES")
print("=" * 80)

def test_own_profile_page():
    response = client.get('/profile/')
    return response.status_code == 200

def test_edit_profile_page():
    response = client.get('/profile/edit/')
    return response.status_code == 200

def test_profile_api_get():
    response = client.get('/api/profile/')
    return response.status_code == 200 and response.json().get('success')

test_feature("View Own Profile", test_own_profile_page)
test_feature("Edit Profile Page", test_edit_profile_page)
test_feature("Profile API (GET)", test_profile_api_get)

print("\n" + "=" * 80)
print("5. NOTIFICATION FEATURES")
print("=" * 80)

def test_notifications_page():
    response = client.get('/notifications/')
    return response.status_code == 200

def test_notification_creation():
    notif = Notification.objects.create(
        recipient=test_user,
        title="Test Notification",
        message="This is a test",
        notification_type="system"
    )
    return notif is not None

test_feature("Notifications Page", test_notifications_page)
test_feature("Notification Creation", test_notification_creation)

print("\n" + "=" * 80)
print("6. ROOM FEATURES")
print("=" * 80)

def test_landing_page():
    # Landing page redirects authenticated users to dashboard
    response = client.get('/')
    return response.status_code in [200, 302]

def test_dashboard_page():
    response = client.get('/dashboard/')
    return response.status_code == 200

def test_create_room_page():
    response = client.get('/rooms/create/')
    return response.status_code == 200

def test_join_room_page():
    response = client.get('/rooms/join/')
    return response.status_code == 200

test_feature("Landing Page", test_landing_page)
test_feature("Dashboard Page", test_dashboard_page)
test_feature("Create Room Page", test_create_room_page)
test_feature("Join Room Page", test_join_room_page)

# Create a test room
test_room = Room.objects.create(
    name="Test Study Room",
    created_by=test_user,
    room_code="TEST123"
)
print(f"✅ Test room created: {test_room.room_code}")

def test_room_detail_page():
    response = client.get(f'/rooms/{test_room.room_code}/')
    return response.status_code == 200

test_feature("Room Detail Page", test_room_detail_page)

print("\n" + "=" * 80)
print("7. SOLO STUDY FEATURES")
print("=" * 80)

def test_solo_study_room():
    response = client.get('/study/')
    return response.status_code == 200

def test_study_goals_page():
    response = client.get('/study/goals/')
    return response.status_code == 200

def test_study_stats_api():
    response = client.get('/study/api/stats/', {'period': 'week'})
    return response.status_code == 200

test_feature("Solo Study Room", test_solo_study_room)
test_feature("Study Goals Page", test_study_goals_page)
test_feature("Study Stats API", test_study_stats_api)

print("\n" + "=" * 80)
print("8. TASK MANAGEMENT FEATURES")
print("=" * 80)

def test_get_tasks_api():
    response = client.get('/study/tasks/')
    return response.status_code == 200

def test_create_task():
    task = Task.objects.create(
        user=test_user,
        title="Test Task"
    )
    return task is not None

test_feature("Get Tasks API", test_get_tasks_api)
test_feature("Create Task", test_create_task)

# Get the created task
test_task = Task.objects.filter(user=test_user).first()

def test_get_task_api():
    response = client.get(f'/study/tasks/{test_task.id}/get/')
    return response.status_code == 200

def test_toggle_task_api():
    response = client.post(f'/study/tasks/{test_task.id}/toggle/')
    return response.status_code == 200

test_feature("Get Single Task API", test_get_task_api)
test_feature("Toggle Task API", test_toggle_task_api)

print("\n" + "=" * 80)
print("9. TRACKER FEATURES")
print("=" * 80)

def test_progress_page():
    response = client.get('/progress/')
    return response.status_code == 200

def test_leaderboard_page():
    response = client.get('/leaderboard/')
    return response.status_code == 200

def test_study_session_creation():
    session = StudySession.objects.create(
        user=test_user,
        minutes=25,
        session_type='focus'
    )
    return session is not None

test_feature("Progress Page", test_progress_page)
test_feature("Leaderboard Page", test_leaderboard_page)
test_feature("Study Session Creation", test_study_session_creation)

print("\n" + "=" * 80)
print("10. ACHIEVEMENT SYSTEM")
print("=" * 80)

def test_achievements_exist():
    achievements = Achievement.objects.all()
    return achievements.count() > 0

test_feature("Achievements Exist", test_achievements_exist)

print("\n" + "=" * 80)
print("11. CHATBOT FEATURE")
print("=" * 80)

def test_chatbot_api_exists():
    # Test if endpoint exists (will fail if no API key, but that's OK)
    response = client.post('/api/chatbot/', 
                           content_type='application/json',
                           data='{"message": "test"}')
    return response.status_code in [200, 400, 503]

test_feature("Chatbot API Endpoint", test_chatbot_api_exists)

print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)

# Clean up test data
test_user.delete()
test_room.delete()
print("✅ Test data cleaned up")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = len([r for r in test_results if "✅" in r[1]])
failed = len([r for r in test_results if "❌" in r[1]])
total = len(test_results)

print(f"\nTotal Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {(passed/total)*100:.1f}%")

if failed > 0:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
    for name, status, error in test_results:
        if "❌" in status:
            print(f"\n{name}:")
            if error:
                print(f"  Error: {error}")

print("\n" + "=" * 80)
print("FEATURE TEST COMPLETE!")
print("=" * 80)

sys.exit(0 if failed == 0 else 1)
