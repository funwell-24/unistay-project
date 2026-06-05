// static/js/notifications.js
// Notification Handling

// Notification State
let notificationState = {
    permission: false,
    socket: null,
    unreadCount: 0,
    notifications: []
};

// Initialize Notifications
document.addEventListener('DOMContentLoaded', function() {
    initNotifications();
});

// Initialize Notification System
function initNotifications() {
    // Request permission for desktop notifications
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            document.getElementById('enableNotifications')?.addEventListener('click', requestNotificationPermission);
        }
        notificationState.permission = Notification.permission === 'granted';
    }
    
    // Load unread count
    loadUnreadCount();
    
    // Setup notification dropdown
    setupNotificationDropdown();
    
    // Start polling for notifications
    startNotificationPolling();
    
    // Mark all as read button
    document.getElementById('markAllRead')?.addEventListener('click', markAllAsRead);
}

// Request Notification Permission
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            notificationState.permission = permission === 'granted';
            if (permission === 'granted') {
                showToast('Notifications enabled!', 'success');
            }
        });
    }
}

// Load Unread Count
async function loadUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count');
        const data = await response.json();
        
        if (data.success) {
            notificationState.unreadCount = data.count;
            updateNotificationBadge(data.count);
        }
    } catch (error) {
        console.error('Error loading unread count:', error);
    }
}

// Update Notification Badge
function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Setup Notification Dropdown
function setupNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.addEventListener('show.bs.dropdown', loadNotifications);
    }
}

// Load Notifications
async function loadNotifications() {
    const container = document.getElementById('notificationsList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/notifications');
        const data = await response.json();
        
        if (data.success) {
            notificationState.notifications = data.notifications;
            updateNotificationsList(data.notifications);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Update Notifications List
function updateNotificationsList(notifications) {
    const container = document.getElementById('notificationsList');
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <i class="fas fa-bell-slash fa-2x text-muted mb-2"></i>
                <p class="mb-0">No notifications</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    notifications.forEach(notification => {
        const icon = getNotificationIcon(notification.type);
        const isRead = notification.is_read;
        
        html += `
            <a href="${notification.link || '#'}" class="dropdown-item notification-item ${!isRead ? 'unread' : ''}" 
               onclick="markAsRead(${notification.id})">
                <div class="d-flex">
                    <div class="me-3">
                        <i class="${icon} fa-lg"></i>
                    </div>
                    <div class="flex-grow-1">
                        <strong>${escapeHtml(notification.title)}</strong>
                        <p class="small mb-0 text-muted">${escapeHtml(notification.message)}</p>
                        <small class="text-muted">${formatRelativeTime(notification.created_at)}</small>
                    </div>
                    ${!isRead ? '<span class="unread-dot"></span>' : ''}
                </div>
            </a>
        `;
    });
    
    container.innerHTML = html;
}

// Get Notification Icon
function getNotificationIcon(type) {
    const icons = {
        'booking': 'fas fa-calendar-check text-primary',
        'message': 'fas fa-envelope text-info',
        'alert': 'fas fa-bell text-warning',
        'system': 'fas fa-cog text-secondary',
        'promotion': 'fas fa-tag text-success'
    };
    return icons[type] || 'fas fa-bell text-secondary';
}

// Mark Notification as Read
async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            notificationState.unreadCount--;
            updateNotificationBadge(notificationState.unreadCount);
            
            // Update local notification
            const notification = notificationState.notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.is_read = true;
            }
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Mark All Notifications as Read
async function markAllAsRead() {
    try {
        const response = await fetch('/api/notifications/mark-all-read', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            notificationState.unreadCount = 0;
            updateNotificationBadge(0);
            
            // Update UI
            document.querySelectorAll('.notification-item').forEach(item => {
                item.classList.remove('unread');
                const dot = item.querySelector('.unread-dot');
                if (dot) dot.remove();
            });
            
            showToast('All notifications marked as read', 'success');
        }
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
}

// Start Notification Polling
function startNotificationPolling() {
    setInterval(async () => {
        if (!document.hidden) {
            await checkForNewNotifications();
        }
    }, 10000); // Check every 10 seconds
}

// Check for New Notifications
async function checkForNewNotifications() {
    try {
        const response = await fetch('/api/notifications/new');
        const data = await response.json();
        
        if (data.success && data.new_count > 0) {
            // Update badge
            notificationState.unreadCount = data.unread_count;
            updateNotificationBadge(notificationState.unreadCount);
            
            // Show desktop notification
            if (notificationState.permission && data.new_notifications.length > 0) {
                data.new_notifications.forEach(notification => {
                    showDesktopNotification(notification);
                });
            }
            
            // Show toast for new notifications
            if (data.new_count === 1) {
                showToast('You have a new notification', 'info');
            } else if (data.new_count > 1) {
                showToast(`You have ${data.new_count} new notifications`, 'info');
            }
            
            // Refresh notifications list if dropdown is open
            const dropdown = document.getElementById('notificationDropdown');
            if (dropdown && dropdown.classList.contains('show')) {
                loadNotifications();
            }
        }
    } catch (error) {
        console.error('Error checking for new notifications:', error);
    }
}

// Show Desktop Notification
function showDesktopNotification(notification) {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;
    
    const options = {
        body: notification.message,
        icon: '/static/images/logo/logo-64.png',
        tag: `notification-${notification.id}`,
        requireInteraction: notification.type === 'booking'
    };
    
    const desktopNotification = new Notification(notification.title, options);
    
    desktopNotification.onclick = function() {
        window.focus();
        if (notification.link) {
            window.location.href = notification.link;
        }
        desktopNotification.close();
    };
    
    // Auto close after 10 seconds
    setTimeout(() => desktopNotification.close(), 10000);
}

// Send Test Notification (for admin)
async function sendTestNotification() {
    try {
        const response = await fetch('/api/notifications/test', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Test notification sent', 'success');
        }
    } catch (error) {
        console.error('Error sending test notification:', error);
    }
}

// Export notification functions
window.notifications = {
    requestPermission: requestNotificationPermission,
    markAsRead,
    markAllAsRead,
    loadNotifications,
    sendTestNotification
};