// AI Tutor Chatbot Widget with Voice Support
class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isListening = false;
        this.isSpeaking = false;
        this.autoSpeak = false; // Auto-speak bot responses
        this.initSpeechAPIs();
        this.init();
    }

    initSpeechAPIs() {
        // Initialize Speech Recognition (Voice Input)
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.container.querySelector('.chatbot-input').value = transcript;
                this.isListening = false;
                this.updateVoiceButton();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
                this.updateVoiceButton();
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceButton();
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
        }

        // Initialize Text-to-Speech (Voice Output)
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
        } else {
            console.warn('Speech synthesis not supported in this browser');
        }
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
            <button class="chatbot-toggle-btn" title="Open AI Tutor">🎓</button>
            <div class="chatbot-window">
                <div class="chatbot-header">
                    <div>
                        <h3>🎓 AI Tutor</h3>
                        <small>Ask me anything about your studies!</small>
                    </div>
                    <div class="chatbot-header-controls">
                        <button class="chatbot-close-btn">✕</button>
                    </div>
                </div>
                <div class="chatbot-messages"></div>
                <div class="chatbot-input-area">
                    <input 
                        type="text" 
                        class="chatbot-input" 
                        placeholder="Type your question..."
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

    toggleVoiceInput() {
        if (!this.recognition) {
            alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        } else {
            this.recognition.start();
            this.isListening = true;
        }
        this.updateVoiceButton();
    }

    updateVoiceButton() {
        const voiceBtn = this.container.querySelector('.chatbot-voice-btn');
        if (this.isListening) {
            voiceBtn.innerHTML = '🔴';
            voiceBtn.title = 'Listening...';
            voiceBtn.classList.add('listening');
        } else {
            voiceBtn.innerHTML = '🎤';
            voiceBtn.title = 'Voice input';
            voiceBtn.classList.remove('listening');
        }
    }



    speak(text) {
        if (!this.synthesis) return;

        // Cancel any ongoing speech
        this.synthesis.cancel();

        // Create utterance - remove HTML tags and decode entities
        const cleanText = text.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.9; // Slightly slower for better comprehension
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Try to use a female voice (more pleasant for tutoring)
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(voice => 
            voice.name.includes('Female') || 
            voice.name.includes('Samantha') ||
            voice.name.includes('Karen')
        );
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        this.synthesis.speak(utterance);
        this.isSpeaking = true;
        
        utterance.onend = () => {
            this.isSpeaking = false;
        };
    }

    toggleSpeak(text, button) {
        if (this.isSpeaking) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            button.classList.remove('active');
        } else {
            this.speak(text);
            button.classList.add('active');
        }
    }

    copyToClipboard(text, button) {
        // Remove HTML tags and decode entities
        const cleanText = text.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        
        navigator.clipboard.writeText(cleanText).then(() => {
            // Show copied feedback
            const originalHTML = button.innerHTML;
            button.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            button.classList.add('success');
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.remove('success');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    }

    toggleLike(likeBtn, dislikeBtn) {
        likeBtn.classList.toggle('active');
        if (likeBtn.classList.contains('active')) {
            dislikeBtn.classList.remove('active');
        }
    }

    toggleDislike(dislikeBtn, likeBtn) {
        dislikeBtn.classList.toggle('active');
        if (dislikeBtn.classList.contains('active')) {
            likeBtn.classList.remove('active');
        }
    }

    regenerateResponse() {
        const messages = this.container.querySelectorAll('.chatbot-message');
        if (messages.length < 2) return;
        
        // Get the last user message
        const userMessages = Array.from(messages).filter(msg => msg.classList.contains('user'));
        if (userMessages.length === 0) return;
        
        const lastUserMessage = userMessages[userMessages.length - 1];
        const messageText = lastUserMessage.querySelector('.chatbot-message-content').textContent;
        
        // Remove the last bot response
        const lastBotMessage = Array.from(messages).reverse().find(msg => msg.classList.contains('bot'));
        if (lastBotMessage) {
            lastBotMessage.remove();
        }
        
        // Resend the message
        this.sendMessageText(messageText);
    }

    async sendMessageText(messageText) {
        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();

            // Add bot response to UI
            this.addMessageToUI(data.reply, 'bot');

            // Speak the response if auto-speak is enabled
            if (this.autoSpeak) {
                this.speak(data.reply);
            }

            // Save message
            this.messages.push({
                user: messageText,
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

            // Speak the response if auto-speak is enabled
            if (this.autoSpeak) {
                this.speak(data.reply);
            }

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
        
        // Format message with line breaks preserved
        const formattedMessage = this.formatMessage(message);
        
        if (sender === 'bot') {
            messageElement.innerHTML = `
                <div class="chatbot-message-wrapper">
                    <div class="chatbot-message-content">${formattedMessage}</div>
                    <div class="chatbot-message-actions">
                        <button class="action-btn copy-btn" title="Copy message">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                        </button>
                        <button class="action-btn speak-btn" title="Read aloud">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"></path>
                            </svg>
                        </button>
                        <button class="action-btn like-btn" title="Good response">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                            </svg>
                        </button>
                        <button class="action-btn dislike-btn" title="Bad response">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                            </svg>
                        </button>
                        <button class="action-btn regenerate-btn" title="Regenerate response">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            
            // Add action button listeners
            const copyBtn = messageElement.querySelector('.copy-btn');
            const speakBtn = messageElement.querySelector('.speak-btn');
            const likeBtn = messageElement.querySelector('.like-btn');
            const dislikeBtn = messageElement.querySelector('.dislike-btn');
            const regenerateBtn = messageElement.querySelector('.regenerate-btn');
            
            copyBtn.addEventListener('click', () => this.copyToClipboard(message, copyBtn));
            speakBtn.addEventListener('click', () => this.toggleSpeak(message, speakBtn));
            likeBtn.addEventListener('click', () => this.toggleLike(likeBtn, dislikeBtn));
            dislikeBtn.addEventListener('click', () => this.toggleDislike(dislikeBtn, likeBtn));
            regenerateBtn.addEventListener('click', () => this.regenerateResponse());
        } else {
            messageElement.innerHTML = `
                <div class="chatbot-message-content">${formattedMessage}</div>
            `;
        }
        
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    formatMessage(text) {
        // Convert double newlines to paragraph breaks, single newlines to <br>
        return this.escapeHtml(text)
            .replace(/\n\n/g, '</p><p>') // Double line breaks = new paragraph
            .replace(/\n/g, '<br>') // Single line breaks = <br>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic text
            .replace(/^(.*)$/, '<p>$1</p>'); // Wrap in paragraph tags
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
                // Display previous messages
                this.messages.forEach(msg => {
                    this.addMessageToUI(msg.user, 'user');
                    this.addMessageToUI(msg.bot, 'bot');
                });
            } catch (e) {
                console.error('Error loading messages:', e);
            }
        }
        
        // Show welcome message only if it's the first time (no messages and no flag)
        const welcomeShown = localStorage.getItem('chatbot-welcome-shown');
        if (!welcomeShown && this.messages.length === 0) {
            this.addMessageToUI(
                'Hey there! 👋 Welcome to our cozy Virtual Cafe! ☕\n\nI\'m your AI tutor and study companion. I can help you with:\n\n📚 Study any subject (Math, Science, Programming, etc.)\n🎯 Create study plans and schedules\n💡 Explain complex topics simply\n✍️ Practice problems and homework help\n🗣️ Use voice input 🎤 or text\n\nWhat would you like to learn today?',
                'bot'
            );
            // Mark welcome message as shown
            localStorage.setItem('chatbot-welcome-shown', 'true');
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const chatbot = new ChatbotWidget();
    
    // Load voices for speech synthesis after a short delay
    if ('speechSynthesis' in window) {
        setTimeout(() => {
            window.speechSynthesis.getVoices();
        }, 100);
    }
});
