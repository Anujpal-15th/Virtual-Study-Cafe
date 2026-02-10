"""
Rooms app URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.home_view, name='home'),
    path('rooms/', views.browse_rooms_view, name='browse_rooms'),
    path('ready-for-study/', views.ready_for_study_view, name='ready_for_study'),
    path('all-study-partners/', views.all_study_partners_view, name='all_study_partners'),
    path('rooms/create/', views.create_room_view, name='create_room'),
    path('rooms/join/', views.join_room_by_code_view, name='join_room_by_code'),
    path('rooms/join/<str:room_code>/', views.join_room_by_code_view, name='join_room_direct'),
    path('rooms/<str:room_code>/', views.room_detail_view, name='room_detail'),
    path('rooms/<str:room_code>/delete/', views.delete_room_view, name='delete_room'),
]
