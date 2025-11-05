// Global variables
let conversationId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 SafarSavvy University Transport AI initialized');
    setupEventListeners();
    initTheme();
});

// Setup event listeners
function setupEventListeners() {
    // Auto-resize textarea
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', autoResizeTextarea);
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Theme handling
function initTheme() {
    try {
        const saved = localStorage.getItem('safarsavvy-theme');
        if (saved === 'dark') {
            document.body.classList.add('dark');
        }
        const btn = document.getElementById('themeToggle');
        if (btn) {
            updateThemeButton(btn);
            btn.addEventListener('click', toggleTheme);
        }
    } catch {}
}

function toggleTheme() {
    document.body.classList.toggle('dark');
    const btn = document.getElementById('themeToggle');
    if (btn) updateThemeButton(btn);
    try {
        localStorage.setItem('safarsavvy-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    } catch {}
}

function updateThemeButton(btn) {
    const dark = document.body.classList.contains('dark');
    btn.innerHTML = dark ? '<i class="fas fa-sun"></i> Theme' : '<i class="fas fa-moon"></i> Theme';
}

// Send message
async function sendMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);
    input.value = '';
    autoResizeTextarea();

    // Show brief loading state first
    const loadingId = addBriefLoadingState();

    try {
        // Use streaming endpoint for real-time response
        const response = await fetch('/query-stream/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: message,
                conversation_id: conversationId
            })
        });

        if (response.ok) {
            // Remove loading state and show typing indicator
            removeBriefLoadingState(loadingId);
            const typingId = addTypingIndicator();
            
            // Handle streaming response
            await handleStreamingResponse(response, typingId);
        } else {
            const error = await response.json();
            removeBriefLoadingState(loadingId);
            addMessage(`Error: ${error.detail}`, false);
        }
        
    } catch (error) {
        console.error('Query error:', error);
        removeBriefLoadingState(loadingId);
        addMessage('Sorry, I encountered an error. Please try again.', false);
    }
}

// Handle streaming response with typing effect
async function handleStreamingResponse(response, typingId) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let currentResponse = '';
    let conversationIdReceived = false;

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        switch (data.type) {
                            case 'conversation_id':
                                if (data.conversation_id) {
                                    conversationId = data.conversation_id;
                                    conversationIdReceived = true;
                                }
                                break;
                                
                            case 'typing':
                                if (data.status === 'start') {
                                    // Typing started
                                } else if (data.status === 'end') {
                                    // Typing ended
                                }
                                break;
                                
                            case 'content':
                                // Add content word by word for realistic typing
                                if (data.chunk) {
                                    currentResponse += data.chunk;
                                    updateTypingResponse(typingId, currentResponse);
                                    
                                    // Smooth scrolling
                                    const chatMessages = document.getElementById('chatMessages');
                                    if (chatMessages) {
                                        chatMessages.scrollTop = chatMessages.scrollHeight;
                                    }
                                }
                                break;
                                
                            case 'complete':
                                // Response complete - finalize the message
                                finalizeTypingResponse(typingId, data.response);
                                return;
                        }
                    } catch (parseError) {
                        console.error('Error parsing streaming data:', parseError);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Streaming error:', error);
        finalizeTypingResponse(typingId, 'Sorry, I encountered an error while streaming the response. Please try again.');
    } finally {
        reader.releaseLock();
    }
}

// Add typing indicator
function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;
    
    const typingDiv = document.createElement('div');
    const typingId = 'typing-' + Date.now();
    typingDiv.id = typingId;
    typingDiv.className = 'message ai-message typing-message';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>SafarSavvy</strong>
                <span class="message-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-text">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
                <div class="typing-text" style="display: none;"></div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingId;
}

// Update typing response text
function updateTypingResponse(typingId, text) {
    const typingDiv = document.getElementById(typingId);
    if (!typingDiv) return;
    
    const typingText = typingDiv.querySelector('.typing-text');
    if (typingText) {
        // Simple text update for smooth typing
        typingText.textContent = text;
        typingText.style.display = 'block';
    }
}

// Finalize typing response and convert to regular message
function finalizeTypingResponse(typingId, finalResponse) {
    const typingDiv = document.getElementById(typingId);
    if (!typingDiv) return;
    
    // Remove the typing message
    typingDiv.remove();
    
    // Add the final formatted message
    addMessage(finalResponse, false);
}

// Add message to chat
function addMessage(text, isUser) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    // Format AI message text for better readability
    let formattedText = text;
    if (!isUser) {
        // Clean up and format AI responses
        formattedText = formatAIResponse(text);
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${isUser ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>${isUser ? 'You' : 'SafarSavvy'}</strong>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-text">${formattedText}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format AI response for better display
function formatAIResponse(text) {
    if (!text) return '';
    try {
        // Parse Markdown to HTML, then sanitize
        const html = marked.parse(text, { breaks: true, mangle: false, headerIds: false });
        const safe = DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
        return safe;
    } catch (e) {
        console.error('Markdown render error:', e);
        // Fallback to escaped text
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Start new chat
function startNewChat() {
    conversationId = null;
    
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <i class="fas fa-bus"></i>
            </div>
            <h3>Welcome to SafarSavvy!</h3>
            <p>I'm your university transport assistant. I can help you with questions about:</p>
            <ul>
                <li>Bus routes and stops</li>
                <li>Timings and schedules</li>
                <li>Student bus pass/registration</li>
                <li>Service updates and policies</li>
            </ul>
            <p><strong>I'm fully trained with SafarSavvy transport information. Ask me anything!</strong></p>
        </div>
    `;
    
    showNotification('New chat started', 'info');
}

// Handle key press
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
function autoResizeTextarea() {
    const textarea = document.getElementById('chatInput');
    if (!textarea) return;
    
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Modal functions
function showSystemInfo() {
    const modal = document.getElementById('systemInfoModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide and remove
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 3000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
        color: #155724;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    
    .notification-info {
        border-left: 4px solid #17a2b8;
        color: #0c5460;
    }
    
    .notification i {
        font-size: 1.2rem;
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Add brief loading state
function addBriefLoadingState() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;
    
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message ai-message loading-message';
    
    loadingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>SafarSavvy</strong>
                <span class="message-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-text">
                <div class="loading-dots">
                    <span class="loading-dot"></span>
                    <span class="loading-dot"></span>
                    <span class="loading-dot"></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return loadingId;
}

// Remove brief loading state
function removeBriefLoadingState(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}
