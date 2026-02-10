"""
Tracker app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('progress/', views.progress_view, name='progress'),
    path('save-session/', views.save_session_view, name='save_session'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    # Schedule Calendar API
    path('api/schedules/', views.get_schedules, name='get_schedules'),
    path('api/schedules/create/', views.create_schedule, name='create_schedule'),
    path('api/schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('api/schedules/<int:schedule_id>/toggle/', views.toggle_schedule, name='toggle_schedule'),
]
