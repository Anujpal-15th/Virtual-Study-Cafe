// Chatbot Widget JavaScript
class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createDOM();
        this.attachEventListeners();
        this.loadMessages();
    }

    createDOM() {
        const container = document.createElement('div');
        container.className = 'chatbot-widget-container';
        container.innerHTML = `
            <button class="chatbot-toggle-btn" title="Open AI Assistant">💬</button>
            <div class="chatbot-window">
                <div class="chatbot-header">
                    <h3>AI Assistant</h3>
                    <button class="chatbot-close-btn">✕</button>
                </div>
                <div class="chatbot-messages"></div>
                <div class="chatbot-input-area">
                    <input 
                        type="text" 
                        class="chatbot-input" 
                        placeholder="Ask me anything..."
                        autocomplete="off"
                    />
                    <button class="chatbot-send-btn">📤</button>
                </div>
            </div>
        `;
        document.body.appendChild(container);
        this.container = container;
    }

    attachEventListeners() {
        const toggleBtn = this.container.querySelector('.chatbot-toggle-btn');
        const closeBtn = this.container.querySelector('.chatbot-close-btn');
        const sendBtn = this.container.querySelector('.chatbot-send-btn');
        const input = this.container.querySelector('.chatbot-input');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.isOpen = true;
        const window = this.container.querySelector('.chatbot-window');
        const toggleBtn = this.container.querySelector('.chatbot-toggle-btn');
        window.classList.add('active');
        toggleBtn.classList.add('active');
        this.container.querySelector('.chatbot-input').focus();
    }

    closeChat() {
        this.isOpen = false;
        const window = this.container.querySelector('.chatbot-window');
        const toggleBtn = this.container.querySelector('.chatbot-toggle-btn');
        window.classList.remove('active');
        toggleBtn.classList.remove('active');
    }

    async sendMessage() {
        const input = this.container.querySelector('.chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to UI
        this.addMessageToUI(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend
            console.log('[Chatbot] Sending message:', message);
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            console.log('[Chatbot] Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[Chatbot] Error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('[Chatbot] Received data:', data);
            
            // Remove typing indicator
            this.removeTypingIndicator();

            // Add bot response to UI
            this.addMessageToUI(data.reply, 'bot');

            // Save message
            this.messages.push({
                user: message,
                bot: data.reply,
                timestamp: new Date().toISOString()
            });
            this.saveMessages();

        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.addMessageToUI(
                'Sorry, I encountered an error. Please try again later.',
                'bot'
            );
        }
    }

    addMessageToUI(message, sender) {
        const messagesDiv = this.container.querySelector('.chatbot-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `chatbot-message ${sender}`;
        messageElement.innerHTML = `<div class="chatbot-message-content">${this.escapeHtml(message)}</div>`;
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    showTypingIndicator() {
        const messagesDiv = this.container.querySelector('.chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message bot';
        typingDiv.innerHTML = `
            <div class="chatbot-message-content">
                <div class="chatbot-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        typingDiv.id = 'typing-indicator';
        messagesDiv.appendChild(typingDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) typingDiv.remove();
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    saveMessages() {
        localStorage.setItem('chatbot-messages', JSON.stringify(this.messages));
    }

    loadMessages() {
        const saved = localStorage.getItem('chatbot-messages');
        if (saved) {
            try {
                this.messages = JSON.parse(saved);
                // Optionally display previous messages
                const messagesDiv = this.container.querySelector('.chatbot-messages');
                this.messages.forEach(msg => {
                    this.addMessageToUI(msg.user, 'user');
                    this.addMessageToUI(msg.bot, 'bot');
                });
            } catch (e) {
                console.error('Error loading messages:', e);
            }
        } else {
            // Show welcome message
            const messagesDiv = this.container.querySelector('.chatbot-messages');
            this.addMessageToUI(
                'Hello! 👋 I\'m your AI Assistant. How can I help you today?',
                'bot'
            );
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const chatbot = new ChatbotWidget();
});
