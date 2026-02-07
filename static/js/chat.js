/**
 * chat.js - Pure Chat Functionality for Global Chat Room
 * 
 * Discord-style chat with real-time messaging only
 * No video calls, no timers, just pure communication
 */

// ===== GLOBAL VARIABLES =====

let chatSocket = null;

// ===== WEBSOCKET SETUP =====

/**
 * Initialize WebSocket connection for chat
 */
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/rooms/${ROOM_CODE}/`;
    
    chatSocket = new WebSocket(wsUrl);
    
    chatSocket.onopen = function(e) {
        console.log('✅ Connected to chat');
        hideEmptyState();
    };
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        handleWebSocketMessage(data);
    };
    
    chatSocket.onclose = function(e) {
        console.log('❌ Disconnected from chat');
        setTimeout(initWebSocket, 3000); // Auto-reconnect
    };
    
    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
}

/**
 * Handle incoming WebSocket messages
 */
function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'chat':
            displayChatMessage(data);
            break;
        
        case 'join':
            displaySystemMessage(`${data.username} joined the chat`);
            updateMemberCount();
            break;
        
        case 'leave':
            displaySystemMessage(`${data.username} left the chat`);
            updateMemberCount();
            break;
    }
}

// ===== MESSAGE DISPLAY =====

/**
 * Display a chat message in bubble style
 */
function displayChatMessage(data) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    
    // Check if this is the current user's message
    const isOwnMessage = data.username === USERNAME;
    messageDiv.className = `message-bubble ${isOwnMessage ? 'own' : ''}`;
    
    // Get avatar URL (use default if not provided)
    const avatarUrl = data.avatar || USER_AVATAR;
    
    messageDiv.innerHTML = `
        <img src="${avatarUrl}" alt="${data.username}" class="message-avatar">
        <div class="message-content">
            <div class="message-sender">${escapeHtml(data.username)}</div>
            <div class="message-text">${escapeHtml(data.message)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    scrollToBottom();
}

/**
 * Display system messages (join/leave notifications)
 */
function displaySystemMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const systemDiv = document.createElement('div');
    systemDiv.className = 'system-message';
    systemDiv.style.cssText = `
        padding: 8px 16px;
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        font-style: italic;
    `;
    systemDiv.textContent = message;
    
    chatMessages.appendChild(systemDiv);
    
    // Auto-scroll to bottom
    scrollToBottom();
}

/**
 * Hide the empty chat state
 */
function hideEmptyState() {
    const emptyState = document.querySelector('.empty-chat');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
}

// ===== MESSAGE SENDING =====

/**
 * Send a chat message through WebSocket
 */
function sendChatMessage(message) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            type: 'chat',
            message: message,
            avatar: USER_AVATAR
        }));
    }
}

// ===== UTILITY FUNCTIONS =====

/**
 * Format timestamp to HH:MM AM/PM
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    });
}

/**
 * Escape HTML to prevent XSS attacks
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update member count display
 */
function updateMemberCount() {
    // Member count will be updated via WebSocket if needed
    // For now, we can leave it static as it's passed from the server
}

/**
 * Force scroll to bottom of chat
 */
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
}

// ===== EVENT LISTENERS =====

/**
 * Initialize chat when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket
    initWebSocket();
    
    // Chat form submission
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        
        if (message && message.length > 0) {
            sendChatMessage(message);
            chatInput.value = '';
            chatInput.focus();
        }
    });
    
    // Auto-focus on input
    chatInput.focus();
    
    // Enter to send, Shift+Enter for new line (optional enhancement)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});

// ===== CLEANUP ON PAGE UNLOAD =====

window.addEventListener('beforeunload', function() {
    if (chatSocket) {
        chatSocket.close();
    }
});
