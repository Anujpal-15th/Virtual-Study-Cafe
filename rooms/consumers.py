"""
WebSocket consumers for real-time chat functionality.
Handles WebSocket connections for the chat rooms.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat messages in rooms.
    """
    
    async def connect(self):
        """
        Called when the websocket connection is opened.
        """
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'chat_{self.room_code}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send join notification to room
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'username': user.username,
                }
            )
    
    async def disconnect(self, close_code):
        """
        Called when the websocket closes.
        """
        # Leave room group
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'username': user.username,
                }
            )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Called when a message is received from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat')
            
            if message_type == 'chat':
                message = data.get('message', '').strip()
                if not message:
                    return
                
                user = self.scope['user']
                if not user.is_authenticated:
                    return
                
                # Save message to database
                await self.save_message(user, message)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': user.username,
                        'user_id': user.id,
                    }
                )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        """
        Called when a chat message is received from the room group.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
        }))
    
    async def user_join(self, event):
        """
        Called when a user joins the room.
        """
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
        }))
    
    async def user_leave(self, event):
        """
        Called when a user leaves the room.
        """
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
        }))
    
    @database_sync_to_async
    def save_message(self, user, message):
        """
        Save chat message to database.
        """
        from .models import Room
        try:
            room = Room.objects.get(room_code=self.room_code)
            # You can create a ChatMessage model if you want to persist messages
            # For now, messages are only stored in real-time
            return True
        except Room.DoesNotExist:
            return False
