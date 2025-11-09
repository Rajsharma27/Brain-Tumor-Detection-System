// Chat Functionality for Brain Tumor Detection Frontend

class ChatManager {
    constructor() {
        this.messages = [];
        this.isTyping = false;
        this.sessionId = this.generateSessionId();
        this.suggestions = [
            "What does my MRI result mean?",
            "What are the symptoms of brain tumors?", 
            "How accurate is AI diagnosis?",
            "What should I do next?",
            "Tell me about treatment options"
        ];
        
        this.init();
    }

    /**
     * Initialize chat functionality
     */
    init() {
        this.setupEventListeners();
        this.displayWelcomeMessage();
        this.renderSuggestions();
        
        console.log('Chat Manager initialized with session ID:', this.sessionId);
    }

    /**
     * Setup event listeners for chat
     */
    setupEventListeners() {
        // Send button
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            chatInput.addEventListener('input', () => {
                this.handleInputChange();
            });
        }

        // Suggestion clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.suggestion-btn')) {
                const suggestion = e.target.textContent.trim();
                this.sendPredefinedMessage(suggestion);
            }
        });
    }

    /**
     * Initialize chat when page becomes active
     */
    initializeChat() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer && this.messages.length === 0) {
            this.displayWelcomeMessage();
            this.renderSuggestions();
        }
    }

    /**
     * Display welcome message
     */
    displayWelcomeMessage() {
        const welcomeMessage = {
            id: this.generateMessageId(),
            type: 'bot',
            content: `Hello! I'm your AI medical assistant. I can help you understand brain tumor analysis, symptoms, treatments, and answer questions about your MRI results.

**Please note:** This AI assistant provides educational information only and should not replace professional medical advice. Always consult with healthcare professionals for medical decisions.

How can I assist you today?`,
            timestamp: new Date()
        };
        
        this.addMessage(welcomeMessage);
        this.renderMessages();
    }

    /**
     * Send message from user input
     */
    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (!chatInput || !sendBtn) return;

        const messageText = chatInput.value.trim();
        
        if (!messageText) {
            UIUtils.showToast('Please enter a message', 'warning');
            return;
        }

        // Disable input while processing
        chatInput.disabled = true;
        sendBtn.disabled = true;

        // Create user message
        const userMessage = {
            id: this.generateMessageId(),
            type: 'user',
            content: messageText,
            timestamp: new Date()
        };

        this.addMessage(userMessage);
        this.renderMessages();
        
        // Clear input
        chatInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to backend
            console.log('Sending message to backend:', messageText);
            const response = await this.sendToBackend(messageText);
            console.log('Received response:', response);
            
            
            this.hideTypingIndicator();
            
            
            const botMessage = {
                id: this.generateMessageId(),
                type: 'bot',
                content: '',  
                timestamp: new Date()
            };

            
            this.addMessage(botMessage);
            this.renderMessages();

            
            await this.typewriterAnimation(botMessage.id, response.content);
            
        } catch (error) {
            console.error('Chat error:', error);
            
            
            this.hideTypingIndicator();
            
            
            const errorMessage = {
                id: this.generateMessageId(),
                type: 'bot',
                content: `I apologize, but I'm experiencing technical difficulties. Please try again later or contact your healthcare provider for immediate assistance.

Error: ${error.message}`,
                timestamp: new Date(),
                isError: true
            };

            this.addMessage(errorMessage);
            this.renderMessages();
            UIUtils.showToast('Failed to send message', 'error');
        }
        
        
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }

    /**
     * 
     * @param {string} message -
     */
    sendPredefinedMessage(message) {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = message;
            this.sendMessage();
        }
    }

    /**
     * 
     * @param {string} message 
     * @returns {Promise<object>} 
     */
    async sendToBackend(message) {
        
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', this.sessionId);

        const response = await APIUtils.makeRequest(
            `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT}`,
            {
                method: 'POST',
                body: formData  
            }
        );

        const result = await response.json();
        
        
        return {
            content: result.bot_response,
            session_id: result.session_id,
            user_message: result.user_message
        };
    }

    /**
     * 
     * @returns {object} -
     */
    getContextData() {
        const context = {
            timestamp: new Date().toISOString()
        };

        
        if (window.app && window.app.analysisResults) {
            context.analysis_results = {
                prediction: window.app.analysisResults.prediction,
                confidence: window.app.analysisResults.confidence,
                probabilities: window.app.analysisResults.probabilities
            };
        }

        
        const patientForm = document.getElementById('patient-form');
        if (patientForm) {
            const formData = FormUtils.extractFormData(patientForm);
            context.patient_info = {
                age: formData.age,
                gender: formData.gender,
                symptoms: formData.symptoms
            };
        }

        return context;
    }

    /**
     * @param {object} message - 
     */
    addMessage(message) {
        this.messages.push(message);
        
        if (this.messages.length > 100) {
            this.messages = this.messages.slice(-50);
        }
    }

    renderMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = this.messages
            .map(message => this.createMessageHTML(message))
            .join('');

        // Scroll to bottom
        this.scrollToBottom();
    }

    /**
     * 
     * @param {object} message
     * @returns {string} 
     */
    createMessageHTML(message) {
        const isUser = message.type === 'user';
        const avatar = isUser ? 'fa-user' : 'fa-robot';
        const messageClass = isUser ? 'user-message' : 'bot-message';
        const errorClass = message.isError ? 'error-message' : '';
        
        const formattedContent = this.formatMessageContent(message.content);
        const timeString = UIUtils.formatDate(message.timestamp);

        return `
            <div class="message ${messageClass} ${errorClass}" data-id="${message.id}">
                <div class="message-avatar">
                    <i class="fas ${avatar}"></i>
                </div>
                <div class="message-content" id="content-${message.id}">
                    ${formattedContent}
                    <span class="message-time">${timeString}</span>
                </div>
            </div>
        `;
    }

    /**
     * Typewriter animation for bot messages
     * @param {string} messageId - Message ID to animate
     * @param {string} fullText - Complete text to type
     */
    async typewriterAnimation(messageId, fullText) {
        const contentElement = document.getElementById(`content-${messageId}`);
        if (!contentElement) return;

        // Clear existing content
        contentElement.innerHTML = '<span class="message-time">' + UIUtils.formatDate(new Date()) + '</span>';
        
        // Create text container
        const textContainer = document.createElement('div');
        textContainer.className = 'typewriter-text';
        contentElement.insertBefore(textContainer, contentElement.firstChild);

        // Split into words for word-by-word animation
        const words = fullText.split(' ');
        let currentWordIndex = 0;
        let animationCancelled = false;
        
        // Add click to skip animation
        const skipAnimation = () => {
            animationCancelled = true;
            textContainer.innerHTML = this.formatMessageContent(fullText);
            const messageIndex = this.messages.findIndex(msg => msg.id === messageId);
            if (messageIndex !== -1) {
                this.messages[messageIndex].content = fullText;
            }
            this.scrollToBottom();
            // Remove click listener
            textContainer.removeEventListener('click', skipAnimation);
            textContainer.style.cursor = 'default';
            textContainer.title = '';
        };

        // Add click listener for skipping
        textContainer.addEventListener('click', skipAnimation);
        textContainer.style.cursor = 'pointer';
        textContainer.title = 'Click to show full message';
        
        return new Promise((resolve) => {
            const typeNextWord = () => {
                if (animationCancelled || currentWordIndex >= words.length) {
                    // Animation complete or cancelled
                    if (!animationCancelled) {
                        textContainer.innerHTML = this.formatMessageContent(fullText);
                        const messageIndex = this.messages.findIndex(msg => msg.id === messageId);
                        if (messageIndex !== -1) {
                            this.messages[messageIndex].content = fullText;
                        }
                    }
                    
                    // Clean up
                    textContainer.removeEventListener('click', skipAnimation);
                    textContainer.style.cursor = 'default';
                    textContainer.title = '';
                    this.scrollToBottom();
                    resolve();
                    return;
                }
                
                // Add next word with cursor
                const currentText = words.slice(0, currentWordIndex + 1).join(' ');
                textContainer.innerHTML = currentText + '<span class="typewriter-cursor">|</span>';
                
                currentWordIndex++;
                this.scrollToBottom();
                
                // Calculate delay based on punctuation for natural pausing
                let delay = 80; // Default delay between words
                const lastWord = words[currentWordIndex - 1];
                if (lastWord) {
                    if (lastWord.endsWith('.') || lastWord.endsWith('!') || lastWord.endsWith('?')) {
                        delay = 300; // Longer pause at sentence endings
                    } else if (lastWord.endsWith(',') || lastWord.endsWith(';') || lastWord.endsWith(':')) {
                        delay = 150; // Medium pause at punctuation
                    }
                }
                
                // Schedule next word
                setTimeout(typeNextWord, delay);
            };
            
            // Start animation
            typeNextWord();
        });
    }

    /**
     * Format message content (handle markdown, links, etc.)
     * @param {string} content - Raw message content
     * @returns {string} - Formatted HTML content
     */
    formatMessageContent(content) {
        // Simple markdown formatting
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>') // Code
            .replace(/\n\n/g, '</p><p>') // Paragraphs
            .replace(/\n/g, '<br>'); // Line breaks

        // Wrap in paragraph tags
        if (!formatted.includes('<p>')) {
            formatted = `<p>${formatted}</p>`;
        }

        // Handle lists
        formatted = formatted.replace(/^[-*+]\s(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        return formatted;
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const messagesContainer = document.getElementById('chat-messages');
        
        if (!messagesContainer) return;

        const typingIndicator = document.createElement('div');
        typingIndicator.id = 'typing-indicator';
        typingIndicator.className = 'message bot-message typing-message';
        typingIndicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingIndicator);
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Handle input change
     */
    handleInputChange() {
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (!chatInput || !sendBtn) return;

        const hasContent = chatInput.value.trim().length > 0;
        sendBtn.disabled = !hasContent;

        // Auto-resize textarea
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    }

    /**
     * Render chat suggestions
     */
    renderSuggestions() {
        const suggestionsContainer = document.querySelector('.chat-suggestions');
        
        if (!suggestionsContainer) return;

        suggestionsContainer.innerHTML = this.suggestions
            .map(suggestion => `
                <button class="suggestion-btn" type="button">
                    ${suggestion}
                </button>
            `).join('');
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    }

    /**
     * Clear chat messages
     */
    clearChat() {
        this.messages = [];
        this.renderMessages();
        this.displayWelcomeMessage();
        UIUtils.showToast('Chat cleared', 'info');
    }

    /**
     * Export chat history
     */
    exportChat() {
        const chatHistory = this.messages.map(msg => ({
            type: msg.type,
            content: msg.content,
            timestamp: msg.timestamp.toISOString()
        }));

        const blob = new Blob(
            [JSON.stringify(chatHistory, null, 2)], 
            { type: 'application/json' }
        );
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        UIUtils.showToast('Chat history exported', 'success');
    }

    /**
     * Generate unique session ID
     * @returns {string} - Session ID
     */
    generateSessionId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Generate unique message ID
     * @returns {string} - Message ID
     */
    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});

// Export for external access
window.ChatManager = ChatManager;