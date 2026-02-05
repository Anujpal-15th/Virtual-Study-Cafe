"""
Main URL Configuration for Virtual Cafe project.
This file routes URLs to the appropriate app views.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Chatbot API
    path('', include('chatbot.urls')),
    
    # Solo Study Room (main feature!)
    path('study/', include('solo.urls')),
    
    # Rooms app URLs (home at root, create room, room detail)
    path('', include('rooms.urls')),
    
    # Accounts app URLs (login, signup, logout, profiles, notifications)
    path('', include('accounts.urls')),
    
    # Tracker app URLs (progress page)
    path('', include('tracker.urls')),
]

# Serve media files (avatars, uploads) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
