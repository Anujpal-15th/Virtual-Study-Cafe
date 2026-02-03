# solo/urls.py
"""
URL patterns for Solo Study Room
"""
from django.urls import path
from . import views, task_views

app_name = 'solo'

urlpatterns = [
    # Main study room
    path('', views.solo_study_room, name='study_room'),
    
    # Study Goals page
    path('goals/', task_views.study_goals_page, name='study_goals'),
    
    # Session management
    path('save-session/', views.save_study_session, name='save_session'),
    path('update-preferences/', views.update_preferences, name='update_preferences'),
    
    # Stats API
    path('api/stats/', views.get_study_stats, name='get_study_stats'),
    
    # Task API endpoints
    path('tasks/', task_views.get_tasks, name='get_tasks'),
    path('tasks/create/', task_views.create_task, name='create_task'),
    path('tasks/<int:task_id>/get/', task_views.get_task, name='get_task'),
    path('tasks/<int:task_id>/update/', task_views.update_task, name='update_task'),
    path('tasks/<int:task_id>/toggle/', task_views.toggle_task, name='toggle_task'),
    path('tasks/<int:task_id>/delete/', task_views.delete_task, name='delete_task'),
]
