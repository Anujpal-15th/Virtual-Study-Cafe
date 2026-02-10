#!/usr/bin/env python
"""
Test script for email verification system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualcafe.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from accounts.models import EmailVerification, UserProfile
from django.contrib.auth.models import User

print("=" * 60)
print("EMAIL VERIFICATION SYSTEM TEST")
print("=" * 60)

# Test 1: Email Configuration
print("\n1. EMAIL CONFIGURATION")
print("-" * 60)
print(f"✓ Backend: {settings.EMAIL_BACKEND}")
print(f"✓ Host: {settings.EMAIL_HOST}")
print(f"✓ Port: {settings.EMAIL_PORT}")
print(f"✓ TLS Enabled: {settings.EMAIL_USE_TLS}")
print(f"✓ SSL Enabled: {settings.EMAIL_USE_SSL}")
print(f"✓ Host User: {settings.EMAIL_HOST_USER}")
print(f"✓ From Email: {settings.DEFAULT_FROM_EMAIL}")

# Test 2: Database Models
print("\n2. DATABASE MODELS")
print("-" * 60)
print(f"✓ EmailVerification model: Available")
print(f"✓ UserProfile model: Available")
print(f"✓ User model: Available")

# Test 3: Check existing data
print("\n3. DATABASE STATUS")
print("-" * 60)
user_count = User.objects.count()
profile_count = UserProfile.objects.count()
verification_count = EmailVerification.objects.count()
print(f"✓ Total Users: {user_count}")
print(f"✓ Total Profiles: {profile_count}")
print(f"✓ Total Verification Tokens: {verification_count}")

# Test 4: Send Test Email
print("\n4. EMAIL SENDING TEST")
print("-" * 60)
try:
    result = send_mail(
        subject='✅ VirtualCafe Email System Test',
        message='This is a test email from your VirtualCafe email verification system. If you receive this, your email configuration is working correctly!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    if result == 1:
        print(f"✅ TEST EMAIL SENT SUCCESSFULLY!")
        print(f"   Sent to: {settings.EMAIL_HOST_USER}")
        print(f"   Check your inbox!")
    else:
        print(f"⚠️  Email send returned: {result}")
except Exception as e:
    print(f"❌ EMAIL SEND FAILED!")
    print(f"   Error: {str(e)}")
    print(f"   Type: {type(e).__name__}")

# Test 5: URL Configuration
print("\n5. URL ROUTES CHECK")
print("-" * 60)
from django.urls import reverse
try:
    print(f"✓ Signup URL: {reverse('signup')}")
    print(f"✓ Login URL: {reverse('login')}")
    print(f"✓ Verification Sent URL: {reverse('verification_sent')}")
    print(f"✓ Resend Verification URL: {reverse('resend_verification')}")
    print(f"✓ URLs configured correctly!")
except Exception as e:
    print(f"❌ URL configuration error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
