"""
ASGI config for virtualcafe project.
This file configures the ASGI application for handling both HTTP and WebSocket connections.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualcafe.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import AFTER Django init to avoid AppRegistryNotReady errors
from rooms.routing import websocket_urlpatterns

# Configure the ASGI application to handle both HTTP and WebSocket
application = ProtocolTypeRouter({
    # Handle traditional HTTP requests
    "http": django_asgi_app,
    
    # Handle WebSocket connections with authentication
    # AuthMiddlewareStack provides user authentication for WebSocket connections
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # WebSocket URL patterns from rooms app
        )
    ),
})
