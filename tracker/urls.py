"""
Tracker app URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('progress/', views.progress_view, name='progress'),
    path('save-session/', views.save_session_view, name='save_session'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
