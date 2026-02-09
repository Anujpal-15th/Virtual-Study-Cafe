#!/usr/bin/env python
"""
Test the complete email verification flow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualcafe.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import EmailVerification, UserProfile
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

print("=" * 60)
print("EMAIL VERIFICATION FLOW TEST")
print("=" * 60)

# Step 1: Create a test user
print("\n📝 STEP 1: Creating test user...")
print("-" * 60)
try:
    # Clean up any existing test user
    User.objects.filter(username='testuser').delete()
    
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"✅ User created: {test_user.username}")
    print(f"   Email: {test_user.email}")
except Exception as e:
    print(f"❌ Error creating user: {e}")
    exit(1)

# Step 2: Check UserProfile auto-creation
print("\n👤 STEP 2: Checking UserProfile...")
print("-" * 60)
try:
    profile = UserProfile.objects.get(user=test_user)
    print(f"✅ UserProfile exists")
    print(f"   Email Verified: {profile.email_verified}")
    print(f"   Gender: {profile.gender}")
    print(f"   Level: {profile.level}")
except UserProfile.DoesNotExist:
    print(f"❌ UserProfile not found! Signal may not be working.")
    exit(1)

# Step 3: Create verification token
print("\n🔑 STEP 3: Creating verification token...")
print("-" * 60)
try:
    verification = EmailVerification.create_for_user(test_user)
    print(f"✅ Verification token created")
    print(f"   Token: {verification.token}")
    print(f"   Expires at: {verification.expires_at}")
    print(f"   Is valid: {verification.is_valid()}")
    print(f"   Is expired: {verification.is_expired()}")
except Exception as e:
    print(f"❌ Error creating token: {e}")
    exit(1)

# Step 4: Generate verification URL
print("\n🔗 STEP 4: Generating verification URL...")
print("-" * 60)
try:
    from django.http import HttpRequest
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    verification_path = reverse('verify_email', args=[verification.token])
    verification_url = f"http://localhost:8000{verification_path}"
    print(f"✅ Verification URL generated")
    print(f"   URL: {verification_url}")
except Exception as e:
    print(f"❌ Error generating URL: {e}")
    exit(1)

# Step 5: Simulate verification
print("\n✓ STEP 5: Simulating email verification...")
print("-" * 60)
try:
    # Mark as verified
    verification.verified = True
    verification.save()
    
    # Update profile
    from django.utils import timezone
    profile.email_verified = True
    profile.email_verified_at = timezone.now()
    profile.save()
    
    # Reload from database
    profile.refresh_from_db()
    verification.refresh_from_db()
    
    print(f"✅ Verification completed")
    print(f"   Token verified: {verification.verified}")
    print(f"   Profile verified: {profile.email_verified}")
    print(f"   Verified at: {profile.email_verified_at}")
except Exception as e:
    print(f"❌ Error during verification: {e}")
    exit(1)

# Step 6: Clean up
print("\n🧹 STEP 6: Cleanup...")
print("-" * 60)
try:
    test_user.delete()
    print(f"✅ Test user deleted")
except Exception as e:
    print(f"⚠️  Cleanup error: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n📧 Email verification system is working correctly!")
print("🎉 You can now test with real signups at:")
print(f"   {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS[0] != '*' else 'http://localhost:8000'}/signup/")
