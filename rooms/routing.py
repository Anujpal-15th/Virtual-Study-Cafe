"""
WebSocket URL routing for rooms app.
Defines WebSocket URL patterns for real-time chat.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/rooms/(?P<room_code>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
