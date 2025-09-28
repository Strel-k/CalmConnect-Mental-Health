/**
 * Real-time Notification System for CalmConnect
 * Handles WebSocket connections, toast notifications, and notification management
 */

class NotificationManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.notificationQueue = [];
        this.unreadCount = 0;
        
        // Initialize notification system
        this.init();
    }
    
    init() {
        this.createNotificationContainer();
        this.connectWebSocket();
        this.bindEvents();
        this.requestNotificationPermission();
        
        // Load initial notifications
        this.loadNotifications();
        
        console.log('🔔 Notification system initialized');
    }
    
    createNotificationContainer() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            container.innerHTML = `
                <style>
                    .toast-container {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        z-index: 10000;
                        max-width: 400px;
                    }
                    
                    .toast {
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        margin-bottom: 10px;
                        padding: 16px;
                        border-left: 4px solid #007bff;
                        animation: slideIn 0.3s ease-out;
                        position: relative;
                        max-width: 100%;
                        word-wrap: break-word;
                    }
                    
                    .toast.success { border-left-color: #28a745; }
                    .toast.warning { border-left-color: #ffc107; }
                    .toast.error { border-left-color: #dc3545; }
                    .toast.urgent { border-left-color: #dc3545; background: #fff5f5; }
                    
                    .toast-header {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 8px;
                    }
                    
                    .toast-icon {
                        font-size: 18px;
                        margin-right: 8px;
                    }
                    
                    .toast-title {
                        font-weight: 600;
                        font-size: 14px;
                        color: #333;
                        flex: 1;
                    }
                    
                    .toast-close {
                        background: none;
                        border: none;
                        font-size: 18px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 20px;
                        height: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .toast-close:hover {
                        color: #666;
                    }
                    
                    .toast-message {
                        font-size: 13px;
                        color: #666;
                        line-height: 1.4;
                        margin-bottom: 8px;
                    }
                    
                    .toast-actions {
                        display: flex;
                        gap: 8px;
                        margin-top: 12px;
                    }
                    
                    .toast-action {
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                    }
                    
                    .toast-action:hover {
                        background: #0056b3;
                        color: white;
                        text-decoration: none;
                    }
                    
                    .toast-time {
                        font-size: 11px;
                        color: #999;
                        margin-top: 4px;
                    }
                    
                    @keyframes slideIn {
                        from {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                        to {
                            transform: translateX(0);
                            opacity: 1;
                        }
                    }
                    
                    @keyframes slideOut {
                        from {
                            transform: translateX(0);
                            opacity: 1;
                        }
                        to {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                    }
                    
                    .toast.removing {
                        animation: slideOut 0.3s ease-in forwards;
                    }
                    
                    /* Notification badge styles */
                    .notification-badge {
                        background: #dc3545;
                        color: white;
                        border-radius: 50%;
                        padding: 2px 6px;
                        font-size: 11px;
                        font-weight: bold;
                        position: absolute;
                        top: -8px;
                        right: -8px;
                        min-width: 18px;
                        height: 18px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                        100% { transform: scale(1); }
                    }
                    
                    /* Connection status indicator */
                    .connection-status {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        padding: 8px 12px;
                        border-radius: 20px;
                        font-size: 12px;
                        font-weight: 500;
                        z-index: 9999;
                        transition: all 0.3s ease;
                    }
                    
                    .connection-status.connected {
                        background: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                    }
                    
                    .connection-status.disconnected {
                        background: #f8d7da;
                        color: #721c24;
                        border: 1px solid #f5c6cb;
                    }
                    
                    .connection-status.connecting {
                        background: #fff3cd;
                        color: #856404;
                        border: 1px solid #ffeaa7;
                    }
                </style>
            `;
            document.body.appendChild(container);
        }
        
        // Create connection status indicator
        if (!document.getElementById('connection-status')) {
            const status = document.createElement('div');
            status.id = 'connection-status';
            status.className = 'connection-status connecting';
            status.textContent = 'Connecting...';
            document.body.appendChild(status);
        }
    }
    
    connectWebSocket() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        console.log('🔌 Connecting to WebSocket:', wsUrl);
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = (event) => {
                console.log('�� WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                
                // Process queued notifications
                this.processNotificationQueue();
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };
            
            this.socket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };
            
        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            this.updateConnectionStatus('disconnected');
            this.scheduleReconnect();
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('❌ Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        this.updateConnectionStatus('connecting');
        
        setTimeout(() => {
            this.connectWebSocket();
        }, delay);
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            
            switch (status) {
                case 'connected':
                    statusElement.textContent = '🟢 Connected';
                    // Hide after 3 seconds
                    setTimeout(() => {
                        statusElement.style.opacity = '0';
                    }, 3000);
                    break;
                case 'disconnected':
                    statusElement.textContent = '🔴 Disconnected';
                    statusElement.style.opacity = '1';
                    break;
                case 'connecting':
                    statusElement.textContent = '🟡 Connecting...';
                    statusElement.style.opacity = '1';
                    break;
            }
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('📨 Received WebSocket message:', data);
        
        switch (data.type) {
            case 'new_notification':
                this.handleNewNotification(data.notification);
                break;
            case 'notification_count':
                this.updateNotificationCount(data.count);
                break;
            case 'notifications_list':
                this.handleNotificationsList(data.notifications);
                break;
            case 'error':
                console.error('❌ WebSocket error:', data.message);
                break;
            default:
                console.log('ℹ️ Unknown message type:', data.type);
        }
    }
    
    handleNewNotification(notification) {
        console.log('🔔 New notification received:', notification);
        
        // Show toast notification
        this.showToast(notification);
        
        // Show browser notification if permitted
        this.showBrowserNotification(notification);
        
        // Update notification count
        this.unreadCount++;
        this.updateNotificationCount(this.unreadCount);
        
        // Play notification sound
        this.playNotificationSound(notification.priority);
        
        // Update dropdown if open
        this.refreshNotificationDropdown();
    }
    
    showToast(notification) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${notification.priority || 'normal'}`;
        toast.dataset.notificationId = notification.id;
        
        const icon = this.getNotificationIcon(notification.type);
        const timeAgo = this.getTimeAgo(new Date(notification.created_at));
        
        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-title">
                    <i class="bx ${icon} toast-icon"></i>
                    ${this.getNotificationTitle(notification.type)}
                </div>
                <button class="toast-close" onclick="notificationManager.closeToast(this)">&times;</button>
            </div>
            <div class="toast-message">${notification.message}</div>
            ${notification.action_url ? `
                <div class="toast-actions">
                    <a href="${notification.action_url}" class="toast-action">
                        ${notification.action_text || 'View'}
                    </a>
                </div>
            ` : ''}
            <div class="toast-time">${timeAgo}</div>
        `;
        
        container.appendChild(toast);
        
        // Auto-remove after delay (longer for urgent notifications)
        const delay = notification.priority === 'urgent' ? 10000 : 5000;
        setTimeout(() => {
            this.closeToast(toast.querySelector('.toast-close'));
        }, delay);
    }
    
    closeToast(closeButton) {
        const toast = closeButton.closest('.toast');
        if (toast) {
            toast.classList.add('removing');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }
    
    showBrowserNotification(notification) {
        if (Notification.permission === 'granted') {
            const browserNotification = new Notification(
                this.getNotificationTitle(notification.type),
                {
                    body: notification.message,
                    icon: '/static/mentalhealth/img/favicon.png',
                    badge: '/static/mentalhealth/img/favicon.png',
                    tag: `notification-${notification.id}`,
                    requireInteraction: notification.priority === 'urgent',
                    silent: false
                }
            );
            
            browserNotification.onclick = () => {
                window.focus();
                if (notification.action_url) {
                    window.location.href = notification.action_url;
                }
                browserNotification.close();
            };
            
            // Auto-close after 5 seconds (unless urgent)
            if (notification.priority !== 'urgent') {
                setTimeout(() => {
                    browserNotification.close();
                }, 5000);
            }
        }
    }
    
    playNotificationSound(priority) {
        // Create audio context if it doesn't exist
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (error) {
                console.log('Audio context not supported');
                return;
            }
        }
        
        // Play different sounds based on priority
        const frequency = priority === 'urgent' ? 800 : 600;
        const duration = priority === 'urgent' ? 200 : 150;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration / 1000);
    }
    
    updateNotificationCount(count) {
        this.unreadCount = count;
        
        // Update all notification badges
        const badges = document.querySelectorAll('.notification-badge, #notificationBadge');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
        
        // Update page title
        this.updatePageTitle(count);
    }
    
    updatePageTitle(count) {
        const originalTitle = document.title.replace(/^\(\d+\) /, '');
        document.title = count > 0 ? `(${count}) ${originalTitle}` : originalTitle;
    }
    
    loadNotifications() {
        fetch('/notifications/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateNotificationCount(data.unread_count || 0);
            }
        })
        .catch(error => {
            console.error('❌ Error loading notifications:', error);
        });
    }
    
    refreshNotificationDropdown() {
        // Trigger refresh of notification dropdown if it's open
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown && dropdown.style.display === 'block') {
            // Call the existing showNotificationDropdown function if it exists
            if (typeof showNotificationDropdown === 'function') {
                showNotificationDropdown();
            }
        }
    }
    
    markAsRead(notificationId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'mark_read',
                notification_id: notificationId
            }));
        }
    }
    
    markAllAsRead() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'mark_all_read'
            }));
        }
    }
    
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('🔔 Notification permission:', permission);
            });
        }
    }
    
    processNotificationQueue() {
        while (this.notificationQueue.length > 0) {
            const notification = this.notificationQueue.shift();
            this.handleNewNotification(notification);
        }
    }
    
    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.unreadCount > 0) {
                // User returned to page, refresh notifications
                this.loadNotifications();
            }
        });
        
        // Handle beforeunload to close WebSocket
        window.addEventListener('beforeunload', () => {
            if (this.socket) {
                this.socket.close();
            }
        });
    }
    
    getNotificationIcon(type) {
        const icons = {
            'appointment': 'bx-calendar',
            'report': 'bx-file',
            'system': 'bx-cog',
            'reminder': 'bx-bell',
            'feedback': 'bx-message-dots',
            'general': 'bx-info-circle'
        };
        return icons[type] || 'bx-info-circle';
    }
    
    getNotificationTitle(type) {
        const titles = {
            'appointment': 'Appointment',
            'report': 'Report',
            'system': 'System',
            'reminder': 'Reminder',
            'feedback': 'Feedback',
            'general': 'Notification'
        };
        return titles[type] || 'Notification';
    }
    
    getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }
    
    // Public API methods
    sendTestNotification() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'test_notification'
            }));
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
    
    reconnect() {
        this.disconnect();
        setTimeout(() => {
            this.connectWebSocket();
        }, 1000);
    }
}

// Initialize notification manager when DOM is ready
let notificationManager;

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    if (document.body.dataset.userAuthenticated !== 'false') {
        notificationManager = new NotificationManager();
        
        // Make it globally available for debugging
        window.notificationManager = notificationManager;
        
        console.log('🔔 Real-time notifications enabled');
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}