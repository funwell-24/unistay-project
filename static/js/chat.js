// static/js/chat.js
// Real-time Chat Functionality

// Chat System State
let chatState = {
    currentConversation: null,
    currentReceiver: null,
    messages: [],
    pollingInterval: null,
    isConnected: false
};

// Initialize Chat
document.addEventListener('DOMContentLoaded', function() {
    initChatSystem();
});

// Initialize Chat System
function initChatSystem() {
    // Load conversations
    loadConversations();
    
    // Setup message form
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', sendMessage);
    }
    
    // Setup real-time polling
    startPolling();
    
    // Mark messages as read when conversation is viewed
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && chatState.currentConversation) {
            markMessagesAsRead(chatState.currentConversation);
        }
    });
}

// Load Conversations
async function loadConversations() {
    const container = document.getElementById('conversationsList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/chat/conversations');
        const data = await response.json();
        
        if (data.success) {
            updateConversationsList(data.conversations);
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

// Update Conversations List
function updateConversationsList(conversations) {
    const container = document.getElementById('conversationsList');
    if (!container) return;
    
    if (conversations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                <p>No conversations yet</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    conversations.forEach(conv => {
        const activeClass = chatState.currentConversation === conv.id ? 'active' : '';
        html += `
            <a href="#" class="list-group-item list-group-item-action ${activeClass}" 
               onclick="selectConversation(${conv.id}, ${conv.other_user_id}, '${escapeHtml(conv.other_user_name)}')">
                <div class="d-flex align-items-center">
                    <img src="${conv.avatar || '/static/images/default-avatar.png'}" 
                         class="rounded-circle me-3" width="40" height="40">
                    <div class="flex-grow-1">
                        <h6 class="mb-0">${escapeHtml(conv.other_user_name)}</h6>
                        <small class="text-muted">${escapeHtml(conv.last_message || 'No messages yet')}</small>
                    </div>
                    ${conv.unread_count > 0 ? `<span class="badge bg-danger rounded-pill">${conv.unread_count}</span>` : ''}
                </div>
            </a>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Select Conversation
function selectConversation(conversationId, userId, userName) {
    chatState.currentConversation = conversationId;
    chatState.currentReceiver = userId;
    
    // Update header
    const chatHeader = document.getElementById('chatHeader');
    if (chatHeader) {
        chatHeader.innerHTML = `
            <div class="d-flex align-items-center">
                <img src="/static/images/default-avatar.png" class="rounded-circle me-2" width="40" height="40">
                <div>
                    <h6 class="mb-0">${escapeHtml(userName)}</h6>
                    <small class="text-muted">Online</small>
                </div>
            </div>
        `;
    }
    
    // Show message input area
    document.getElementById('messageInputArea').style.display = 'block';
    
    // Load messages
    loadMessages(conversationId);
    
    // Mark as read
    markMessagesAsRead(conversationId);
}

// Load Messages
async function loadMessages(conversationId) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    try {
        const response = await fetch(`/api/chat/messages/${conversationId}`);
        const data = await response.json();
        
        if (data.success) {
            chatState.messages = data.messages;
            updateMessagesUI(data.messages);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

// Update Messages UI
function updateMessagesUI(messages) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-comment-dots fa-3x text-muted mb-3"></i>
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    messages.forEach(message => {
        const isSender = message.sender_id === window.currentUserId;
        html += `
            <div class="chat-message ${isSender ? 'sent' : 'received'}">
                <div class="message-bubble ${isSender ? 'sent' : 'received'}">
                    <p class="mb-0">${escapeHtml(message.message)}</p>
                    <small class="${isSender ? 'text-white-50' : 'text-muted'}">
                        ${formatRelativeTime(message.created_at)}
                    </small>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    scrollToBottom();
}

// Send Message
async function sendMessage(event) {
    event.preventDefault();
    
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    if (!chatState.currentReceiver) {
        showToast('Please select a conversation first', 'warning');
        return;
    }
    
    // Clear input
    messageInput.value = '';
    
    // Add message to UI optimistically
    addMessageToUI(message, true);
    
    try {
        const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: chatState.currentReceiver,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showToast('Failed to send message', 'error');
            // Remove optimistic message
            removeLastMessage();
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('An error occurred', 'error');
        removeLastMessage();
    }
}

// Add Message to UI (optimistic update)
function addMessageToUI(message, isSender) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    // Remove empty state if present
    if (container.querySelector('.text-center')) {
        container.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isSender ? 'sent' : 'received'}`;
    messageDiv.innerHTML = `
        <div class="message-bubble ${isSender ? 'sent' : 'received'}">
            <p class="mb-0">${escapeHtml(message)}</p>
            <small class="${isSender ? 'text-white-50' : 'text-muted'}">Just now</small>
        </div>
    `;
    
    container.appendChild(messageDiv);
    scrollToBottom();
}

// Remove Last Message (on error)
function removeLastMessage() {
    const container = document.getElementById('messagesContainer');
    if (container && container.lastChild) {
        container.removeChild(container.lastChild);
    }
}

// Mark Messages as Read
async function markMessagesAsRead(conversationId) {
    try {
        await fetch(`/api/chat/mark-read/${conversationId}`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error marking messages as read:', error);
    }
}

// Scroll to Bottom of Chat
function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// Start Real-time Polling
function startPolling() {
    if (chatState.pollingInterval) {
        clearInterval(chatState.pollingInterval);
    }
    
    chatState.pollingInterval = setInterval(async () => {
        if (chatState.currentConversation && !document.hidden) {
            await checkForNewMessages();
        }
        await loadConversations(); // Update conversation list for new messages
    }, 3000); // Poll every 3 seconds
}

// Check for New Messages
async function checkForNewMessages() {
    try {
        const response = await fetch(`/api/chat/messages/${chatState.currentConversation}?since=${chatState.messages.length}`);
        const data = await response.json();
        
        if (data.success && data.messages.length > 0) {
            // Add new messages to UI
            data.messages.forEach(message => {
                if (!chatState.messages.find(m => m.id === message.id)) {
                    chatState.messages.push(message);
                    addMessageToUI(message.message, message.sender_id === window.currentUserId);
                }
            });
            
            // Mark as read
            markMessagesAsRead(chatState.currentConversation);
        }
    } catch (error) {
        console.error('Error checking for new messages:', error);
    }
}

// Stop Polling (cleanup)
function stopPolling() {
    if (chatState.pollingInterval) {
        clearInterval(chatState.pollingInterval);
        chatState.pollingInterval = null;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopPolling();
});

// Export chat functions
window.chat = {
    selectConversation,
    sendMessage,
    loadConversations
};