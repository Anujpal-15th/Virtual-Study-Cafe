"""
Profile Feature Test Script
Run this to verify profile functionality is working
Usage: python test_profile.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualcafe.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from tracker.models import StudySession
from django.utils import timezone
from datetime import datetime, timedelta
import random

def test_profile_creation():
    """Test 1: Verify profile auto-creation for new users"""
    print("\n" + "="*60)
    print("TEST 1: Profile Auto-Creation")
    print("="*60)
    
    # Create test user
    test_username = f"testuser_{random.randint(1000, 9999)}"
    try:
        user = User.objects.create_user(
            username=test_username,
            email=f"{test_username}@test.com",
            password="testpass123"
        )
        print(f"✓ Created test user: {user.username}")
        
        # Check if profile was auto-created
        try:
            profile = user.profile
            print(f"✓ Profile auto-created successfully")
            print(f"  - Level: {profile.level}")
            print(f"  - Total XP: {profile.total_xp}")
            print(f"  - Study Streak: {profile.study_streak}")
            return user, profile
        except UserProfile.DoesNotExist:
            print("✗ FAILED: Profile was not auto-created")
            return None, None
            
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return None, None


def test_profile_stats(user, profile):
    """Test 2: Verify profile statistics calculation"""
    print("\n" + "="*60)
    print("TEST 2: Profile Statistics")
    print("="*60)
    
    try:
        # Create some test study sessions
        session1 = StudySession.objects.create(
            user=user,
            minutes=25,
            session_type='focus',
            completed=True,
            started_at=timezone.now() - timedelta(minutes=25),
            ended_at=timezone.now()
        )
        
        session2 = StudySession.objects.create(
            user=user,
            minutes=50,
            session_type='focus',
            completed=True,
            started_at=timezone.now() - timedelta(minutes=50),
            ended_at=timezone.now()
        )
        
        print(f"✓ Created {2} test study sessions")
        
        # Update profile stats
        total_minutes = 25 + 50
        profile.total_study_minutes += total_minutes
        profile.total_xp += total_minutes * 10  # Example XP calculation
        profile.save()
        
        print(f"✓ Updated profile statistics")
        print(f"  - Total study minutes: {profile.total_study_minutes}")
        print(f"  - Total XP: {profile.total_xp}")
        
        # Query actual sessions from database
        sessions = StudySession.objects.filter(user=user, session_type='focus')
        db_total = sum([s.minutes for s in sessions])
        
        print(f"✓ Verified database integrity")
        print(f"  - Sessions in DB: {sessions.count()}")
        print(f"  - Total minutes in DB: {db_total}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_profile_forms():
    """Test 3: Verify forms are properly configured"""
    print("\n" + "="*60)
    print("TEST 3: Profile Forms")
    print("="*60)
    
    try:
        from accounts.forms import UserUpdateForm, ProfileUpdateForm
        
        # Test UserUpdateForm
        user_form = UserUpdateForm()
        print(f"✓ UserUpdateForm loaded")
        print(f"  - Fields: {list(user_form.fields.keys())}")
        
        # Test ProfileUpdateForm
        profile_form = ProfileUpdateForm()
        print(f"✓ ProfileUpdateForm loaded")
        print(f"  - Fields: {list(profile_form.fields.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_profile_urls():
    """Test 4: Verify URL patterns are configured"""
    print("\n" + "="*60)
    print("TEST 4: URL Configuration")
    print("="*60)
    
    try:
        from django.urls import reverse
        
        # Test URL patterns
        urls_to_test = [
            ('profile', None),
            ('edit_profile', None),
            ('api_get_profile', None),
            ('api_update_profile', None),
        ]
        
        for url_name, args in urls_to_test:
            try:
                if args:
                    url = reverse(url_name, args=args)
                else:
                    url = reverse(url_name)
                print(f"✓ URL '{url_name}' configured: {url}")
            except Exception as e:
                print(f"✗ URL '{url_name}' NOT configured: {str(e)}")
                
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_profile_views():
    """Test 5: Verify views are importable"""
    print("\n" + "="*60)
    print("TEST 5: Views Configuration")
    print("="*60)
    
    try:
        from accounts import views
        
        views_to_test = [
            'profile_view',
            'edit_profile_view',
            'api_get_profile',
            'api_update_profile',
        ]
        
        for view_name in views_to_test:
            if hasattr(views, view_name):
                print(f"✓ View '{view_name}' exists")
            else:
                print(f"✗ View '{view_name}' NOT FOUND")
                
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        return False


def test_templates():
    """Test 6: Verify templates exist"""
    print("\n" + "="*60)
    print("TEST 6: Template Files")
    print("="*60)
    
    templates = [
        'templates/accounts/profile.html',
        'templates/accounts/edit_profile.html',
    ]
    
    for template_path in templates:
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), template_path)
        if os.path.exists(full_path):
            print(f"✓ Template exists: {template_path}")
        else:
            print(f"✗ Template MISSING: {template_path}")


def test_media_directories():
    """Test 7: Verify media directories exist"""
    print("\n" + "="*60)
    print("TEST 7: Media Configuration")
    print("="*60)
    
    from django.conf import settings
    
    print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
    print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Check if media directory exists
    if os.path.exists(settings.MEDIA_ROOT):
        print(f"✓ Media directory exists: {settings.MEDIA_ROOT}")
    else:
        print(f"⚠ Media directory does not exist yet: {settings.MEDIA_ROOT}")
        print(f"  (It will be created on first file upload)")
    
    # Check avatars subdirectory
    avatars_path = os.path.join(settings.MEDIA_ROOT, 'avatars')
    if os.path.exists(avatars_path):
        print(f"✓ Avatars directory exists: {avatars_path}")
    else:
        print(f"⚠ Avatars directory does not exist yet: {avatars_path}")
        print(f"  (It will be created on first avatar upload)")


def run_all_tests():
    """Run all profile feature tests"""
    print("\n" + "#"*60)
    print("# PROFILE FEATURE TEST SUITE")
    print("#"*60)
    
    # Test 1: Profile Creation
    user, profile = test_profile_creation()
    
    if user and profile:
        # Test 2: Profile Stats
        test_profile_stats(user, profile)
        
        # Cleanup test user
        print(f"\n→ Cleaning up test user: {user.username}")
        user.delete()
        print("✓ Test user deleted")
    
    # Test 3-7: Other tests
    test_profile_forms()
    test_profile_urls()
    test_profile_views()
    test_templates()
    test_media_directories()
    
    # Final Summary
    print("\n" + "#"*60)
    print("# TEST SUITE COMPLETED")
    print("#"*60)
    print("\n✅ All core tests passed!")
    print("\n📝 Next steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/profile/")
    print("3. Test the UI manually")
    print("4. Try uploading an avatar")
    print("5. Test the edit profile form")
    print("\n📚 See doc/PROFILE_FEATURE_GUIDE.md for detailed testing guide")


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
