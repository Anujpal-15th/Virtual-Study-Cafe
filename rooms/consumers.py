"""
WebSocket consumers for real-time chat functionality.
Handles WebSocket connections, messages, and room membership.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat in study rooms.
    Manages user connections, message broadcasting, and room membership.
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Add user to room group and accept the connection.
        """
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'chat_{self.room_code}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept WebSocket connection
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat room'
        }))
        
        # Notify others that user joined (if authenticated)
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'username': self.user.username,
                }
            )
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Remove user from room group.
        """
        # Notify others that user left (if authenticated)
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'username': self.user.username,
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages
from client.
        Process different message types and broadcast to room group.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat')
            
            if message_type == 'chat':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'webrtc_ice':
                await self.handle_ice_candidate(data)
            elif message_type == 'webrtc_offer':
                await self.handle_webrtc_offer(data)
            elif message_type == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif message_type == 'timer':
                await self.handle_timer_event(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
    
    async def handle_chat_message(self, data):
        """Handle regular chat messages"""
        message = data.get('message', '')
        
        if not message.strip():
            return
        
        if not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You must be logged in to send messages'
            }))
            return
        
        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'user_id': self.user.id,
                'timestamp': timestamp,
            }
        )
    
    async def handle_typing(self, data):
        """Handle typing indicators"""
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', False),
                }
            )
    
    async def handle_ice_candidate(self, data):
        """Handle WebRTC ICE candidates for video chat"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_ice_message',
                'candidate': data.get('candidate'),
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
            }
        )
    
    async def handle_webrtc_offer(self, data):
        """Handle WebRTC offers for video chat"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer_message',
                'offer': data.get('offer'),
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
            }
        )
    
    async def handle_webrtc_answer(self, data):
        """Handle WebRTC answers for video chat"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer_message',
                'answer': data.get('answer'),
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
            }
        )
    
    async def handle_timer_event(self, data):
        """Handle timer events"""
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'timer_message',
                    'action': data.get('action'),
                    'username': self.user.username,
                }
            )
    
    # Group message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event.get('timestamp', ''),
        }))
    
    async def user_join(self, event):
        """Send user join notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
        }))
    
    async def user_leave(self, event):
        """Send user leave notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
        }))
    
    async def user_typing(self, event):
        """Send typing indicator to WebSocket"""
        # Don't send typing indicator back to the sender
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))
    
    async def webrtc_ice_message(self, event):
        """Send ICE candidate to WebSocket"""
        # Don't send back to sender
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_ice',
                'candidate': event['candidate'],
                'username': event['username'],
            }))
    
    async def webrtc_offer_message(self, event):
        """Send WebRTC offer to WebSocket"""
        # Don't send back to sender
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_offer',
                'offer': event['offer'],
                'username': event['username'],
            }))
    
    async def webrtc_answer_message(self, event):
        """Send WebRTC answer to WebSocket"""
        # Don't send back to sender
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_answer',
                'answer': event['answer'],
                'username': event['username'],
            }))
    
    async def timer_message(self, event):
        """Send timer event to WebSocket"""
        # Don't send back to sender
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'timer',
                'action': event['action'],
                'username': event['username'],
            }))
