/**
 * Real-time Notification System for CalmConnect
 * Handles WebSocket connections, toast notifications, and notification management
 */
console.log('🔔 notifications.js loaded successfully - version 1.2.0');

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
        // Remove immediate WebSocket connection - will connect lazily
        this.bindEvents();
        this.requestNotificationPermission();

        // Load initial notifications (without WebSocket)
        this.loadNotifications();

        console.log('🔔 Notification system initialized (lazy loading)');

        // Set up lazy connection triggers
        this.setupLazyConnection();
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
    
    handleNotificationAction(type, actionText, actionUrl, notificationId, followupRequestId, metadata) {
        console.log('🔗 Handling notification action:', { type, actionText, actionUrl, notificationId, followupRequestId, metadata });
        console.log('🔗 Metadata type:', typeof metadata, 'value:', metadata);

        // Mark notification as read
        this.markAsRead(notificationId);

        // Handle follow-up notifications based on user type
        if (type === 'followup') {
            console.log('🎯 Handling follow-up notification:', notificationId, 'actionUrl:', actionUrl, 'followupRequestId:', followupRequestId);

            // Parse metadata if it's a string
            let parsedMetadata = metadata || {};
            console.log('🔗 Initial parsedMetadata:', parsedMetadata, 'type:', typeof parsedMetadata);
            if (typeof parsedMetadata === 'string') {
                try {
                    parsedMetadata = JSON.parse(parsedMetadata);
                    console.log('🔗 Parsed metadata from string:', parsedMetadata);
                } catch (e) {
                    console.warn('Failed to parse metadata in handleNotificationAction:', e);
                    parsedMetadata = {};
                }
            }

            console.log('📋 Final metadata for notification routing:', parsedMetadata);

            // Prioritize user_type over action_url for determining notification type
            const isStudentNotification = parsedMetadata.user_type === 'student' || (!parsedMetadata.user_type && (!actionUrl || actionUrl === '#'));
            const hasAppointment = parsedMetadata.appointment_id || (parsedMetadata.scheduled_date && parsedMetadata.scheduled_time);

            console.log('📋 Notification routing decision:', {
                isStudentNotification,
                hasAppointment,
                user_type: parsedMetadata.user_type,
                appointment_id: parsedMetadata.appointment_id,
                scheduled_date: parsedMetadata.scheduled_date,
                scheduled_time: parsedMetadata.scheduled_time,
                followup_request_id: parsedMetadata.followup_request_id
            });

            if (isStudentNotification) {
                // Student notification - show consent modal
                console.log('📋 Student follow-up notification - showing consent modal');
                try {
                    if (followupRequestId) {
                        console.log('✅ Using direct followupRequestId:', followupRequestId);
                        this.showFollowupConsentModal(followupRequestId);
                    } else {
                        console.log('⚠️ No followupRequestId, using fallback method');
                        this.showFollowupConsentModal({ action_url: actionUrl, id: notificationId, action_text: actionText });
                    }
                    return; // Prevent default navigation
                } catch (error) {
                    console.error('❌ Error showing follow-up modal:', error);
                    this.showModalError('Failed to load follow-up details. Please try again.');
                    return;
                }
            } else {
                // Counselor notification - check if scheduled or needs scheduling
                if (hasAppointment) {
                    // Scheduled follow-up - show session details modal
                    console.log('📅 Counselor follow-up notification - showing scheduled session details');
                    try {
                        if (followupRequestId) {
                            console.log('✅ Using direct followupRequestId:', followupRequestId);
                            this.showScheduledFollowupModal(followupRequestId, metadata);
                        } else {
                            console.error('❌ Could not extract followup request ID for scheduled session');
                            this.showModalError('Invalid follow-up notification. Please refresh the page.');
                        }
                        return; // Prevent default navigation
                    } catch (error) {
                        console.error('❌ Error showing scheduled follow-up modal:', error);
                        this.showModalError('Failed to load follow-up session details. Please try again.');
                        return;
                    }
                } else {
                    // Unscheduled follow-up - show scheduling modal
                    console.log('📅 Counselor follow-up notification - showing scheduling modal');
                    try {
                        if (followupRequestId) {
                            console.log('✅ Using direct followupRequestId:', followupRequestId);
                            this.showFollowupSchedulingModal(followupRequestId);
                        } else {
                            // Try to extract from actionUrl
                            const urlMatch = actionUrl && actionUrl.match(/\/followup\/(\d+)\//);
                            const requestId = urlMatch ? urlMatch[1] : null;
                            if (requestId) {
                                this.showFollowupSchedulingModal(requestId);
                            } else {
                                console.error('❌ Could not extract followup request ID');
                                this.showModalError('Invalid follow-up notification. Please refresh the page.');
                            }
                        }
                        return; // Prevent default navigation
                    } catch (error) {
                        console.error('❌ Error showing follow-up scheduling modal:', error);
                        this.showModalError('Failed to load follow-up scheduling details. Please try again.');
                        return;
                    }
                }
            }
        }

        // For non-followup notifications, navigate to URL if available
        if (actionUrl && actionUrl !== '#') {
            console.log('🔗 Navigating to URL:', actionUrl);
            window.location.href = actionUrl;
        }
    }

    showFollowupConsentModal(notification) {
        console.log('📋 Showing follow-up modal with notification:', notification, 'type:', typeof notification);
        console.log('📋 notificationManager exists:', !!window.notificationManager);
        console.log('📋 this is notificationManager:', this === window.notificationManager);

        // Remove any existing modal with the same ID
        const existingModal = document.getElementById('followup-consent-modal');
        if (existingModal) {
            existingModal.remove();
        }

        let followupRequestId = null;

        // Handle different input types
        if (typeof notification === 'string') {
            // Legacy: extract from URL string
            const urlMatch = notification.match(/\/followup\/(\d+)\/(?:consent|schedule)\//);
            followupRequestId = urlMatch ? urlMatch[1] : null;
            console.log('📋 Path 1: Extracted followup request ID from URL string:', followupRequestId);
        } else if (typeof notification === 'number' || (typeof notification === 'string' && /^\d+$/.test(notification))) {
            // Direct followup request ID
            followupRequestId = String(notification);
            console.log('📋 Path 2: Using direct followup request ID:', followupRequestId);
        } else if (typeof notification === 'object' && notification.type === 'followup') {
            // New: extract from notification metadata
            followupRequestId = notification.metadata && notification.metadata.followup_request_id;
            console.log('📋 Path 3: Extracted followup request ID from metadata:', followupRequestId);

            // Fallback: try to extract from action_url if metadata doesn't have it
            if (!followupRequestId && notification.action_url) {
                const urlMatch = notification.action_url.match(/\/followup\/(\d+)\/(?:consent|schedule)\//);
                followupRequestId = urlMatch ? urlMatch[1] : null;
                console.log('📋 Path 3b: Fallback extracted followup request ID from action_url:', followupRequestId);
            }
        } else {
            console.log('📋 Path 4: Unknown notification type/format:', typeof notification, notification);
        }

        console.log('📋 Final followup request ID:', followupRequestId);

        // Create modal for follow-up consent
        const modal = document.createElement('div');
        modal.id = 'followup-consent-modal';
        modal.className = 'modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        `;
        modal.innerHTML = `
            <div class="modal-content followup-consent-modal" style="
                background: white;
                border-radius: 12px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            ">
                <div class="modal-header" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #eee;
                ">
                    <h3 style="margin: 0; color: #2c3e50;">Follow-up Session Acceptance</h3>
                    <button class="modal-close" onclick="notificationManager.closeFollowupConsentModal()" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <div class="loading-spinner" id="modalLoading" style="
                        text-align: center;
                        padding: 40px;
                    ">
                        <div class="spinner" style="
                            border: 4px solid #f3f3f3;
                            border-top: 4px solid #2ecc71;
                            border-radius: 50%;
                            width: 40px;
                            height: 40px;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 20px;
                        "></div>
                        <p>Loading follow-up details...</p>
                    </div>
                    <div id="modalContent" style="display: none;">
                        <!-- Content will be loaded here -->
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        console.log('Modal appended to body');

        // Load modal content if we have a valid ID
        if (followupRequestId) {
            this.loadFollowupConsentContent(followupRequestId);
        } else {
            // Show error if no valid ID
            this.showModalError('Invalid follow-up notification. Please refresh the page.');
        }
    }

    loadFollowupConsentContent(followupRequestId) {
        console.log('Loading follow-up content for ID:', followupRequestId);
        console.log('Full URL:', `/followup/${followupRequestId}/consent/`);

        // Create AbortController for timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
            console.log('Fetch request timed out');
            this.showModalError('Request timed out. Please check your connection and try again.');
        }, 10000); // 10 second timeout

        console.log('Starting fetch...');
        fetch(`/followup/${followupRequestId}/consent/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            console.log('Fetch completed. Response status:', response.status, 'Response ok:', response.ok);
            console.log('Response headers:', response.headers);

            if (!response.ok) {
                console.log('Response not ok, throwing error');
                // Try to get error message from response
                return response.text().then(text => {
                    try {
                        const errorData = JSON.parse(text);
                        throw new Error(errorData.error || `HTTP ${response.status}`);
                    } catch (e) {
                        throw new Error(text || `HTTP ${response.status}`);
                    }
                });
            }

            console.log('Response is ok, parsing JSON...');
            return response.json();
        })
        .then(data => {
            console.log('Received JSON data:', data);

            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }

            if (data.success) {
                console.log('Data success, rendering content...');
                try {
                    this.renderFollowupConsentContent(data);
                    console.log('Content rendered successfully');
                } catch (error) {
                    console.error('Error rendering follow-up content:', error);
                    this.showModalError('Failed to display follow-up details. The data may be corrupted.');
                }
            } else {
                console.log('Data not success, showing error:', data.error);
                // Handle specific error cases
                const errorMessage = data.error || 'Failed to load follow-up details';
                if (errorMessage.includes('not available') || errorMessage.includes('not found')) {
                    this.showModalError('This follow-up session is no longer available. It may have been cancelled or completed.');
                } else if (errorMessage.includes('permission') || errorMessage.includes('denied')) {
                    this.showModalError('You do not have permission to view this follow-up session.');
                } else {
                    this.showModalError(errorMessage);
                }
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error loading follow-up consent modal:', error);
            console.error('Error message:', error.message);
            console.error('Error name:', error.name);

            // Handle different error types
            if (error.name === 'AbortError') {
                console.log('Request was aborted (timeout)');
                this.showModalError('Request timed out. Please check your connection and try again.');
            } else if (error.message && error.message.includes('404')) {
                this.showModalError('This follow-up session is no longer available.');
            } else if (error.message && error.message.includes('403')) {
                this.showModalError('You do not have permission to view this follow-up session.');
            } else if (error.message && error.message.includes('500')) {
                this.showModalError('Server error occurred. Please try again later.');
            } else if (error.message && error.message.includes('Invalid response format')) {
                this.showModalError('Received invalid data from server. Please refresh the page.');
            } else {
                this.showModalError('Failed to load follow-up details. Please check your connection and try again.');
            }
        });
    }

    renderFollowupConsentContent(data) {
        const modalContent = document.getElementById('modalContent');
        const loading = document.getElementById('modalLoading');

        if (!modalContent || !loading) {
            console.error('Modal elements not found');
            this.showModalError('Modal display error. Please refresh the page.');
            return;
        }

        try {
            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data structure received');
            }

            const followup = data.followup_request;
            const appointment = data.appointment;
            const counselor = data.counselor;

            // Validate required data
            if (!followup || !followup.id) {
                throw new Error('Follow-up request data is missing or invalid');
            }

            // Helper function to safely handle services
            const formatServices = (services) => {
                try {
                    if (!services) return 'TBD';
                    if (Array.isArray(services)) return services.join(', ');
                    if (typeof services === 'string') return services;
                    return String(services);
                } catch (e) {
                    console.warn('Error formatting services:', e);
                    return 'TBD';
                }
            };

            // Safe data extraction with fallbacks
            const counselorName = (counselor && counselor.name) ? counselor.name : 'Unknown Counselor';
            const counselorUnit = (counselor && counselor.unit) ? counselor.unit : 'Unknown Unit';
            const counselorRank = (counselor && counselor.rank) ? counselor.rank : 'Unknown Rank';
            const counselorImage = (counselor && counselor.image_url) ? counselor.image_url : '/static/img/default.jpg';

            const appointmentDate = (appointment && appointment.date) ? appointment.date : 'TBD';
            const appointmentTime = (appointment && appointment.time) ? appointment.time : 'TBD';
            const appointmentType = (appointment && appointment.session_type) ? appointment.session_type : 'TBD';
            const appointmentServices = formatServices(appointment ? appointment.services : null);

            modalContent.innerHTML = `
                <div class="followup-details">
                    <div class="counselor-info">
                        <img src="${counselorImage}" alt="${counselorName}" class="counselor-avatar" onerror="this.src='/static/img/default.jpg'">
                        <div class="counselor-details">
                            <h4>${counselorName}</h4>
                            <p>${counselorUnit}</p>
                            <p>${counselorRank}</p>
                        </div>
                    </div>

                    <div class="appointment-details">
                        <h4>Appointment Details</h4>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span class="detail-value">${appointmentDate}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span class="detail-value">${appointmentTime}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">${appointmentType}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Services:</span>
                            <span class="detail-value">${appointmentServices}</span>
                        </div>
                    </div>

                    <div class="consent-question">
                        <h4>Do you accept this follow-up session?</h4>
                        <p>Your participation will help continue your counseling journey.</p>
                    </div>

                    <form id="consentForm" method="post">
                        <input type="hidden" name="consent_given" id="consentInput" value="">
                        <div class="action-buttons">
                            <button type="button" class="consent-btn" id="modalConsentBtn">
                                <i class="bx bx-check"></i> Yes, I Accept
                            </button>
                            <button type="button" class="decline-btn" id="modalDeclineBtn">
                                <i class="bx bx-x"></i> No, Decline
                            </button>
                        </div>
                    </form>
                </div>
            `;

            // Add content styles
            const contentStyle = document.createElement('style');
            contentStyle.textContent = `
                .followup-details {
                    max-width: 100%;
                }

                .counselor-info {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }

                .counselor-avatar {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 2px solid #2ecc71;
                }

                .counselor-details h4 {
                    margin: 0 0 5px 0;
                    color: #2c3e50;
                }

                .counselor-details p {
                    margin: 2px 0;
                    color: #666;
                    font-size: 14px;
                }

                .appointment-details {
                    background: white;
                    border: 1px solid #eee;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                }

                .appointment-details h4 {
                    margin: 0 0 15px 0;
                    color: #2c3e50;
                }

                .detail-row {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }

                .detail-row:last-child {
                    margin-bottom: 0;
                }

                .detail-label {
                    font-weight: 500;
                    color: #555;
                }

                .detail-value {
                    font-weight: 600;
                    color: #2c3e50;
                }

                .consent-question {
                    text-align: center;
                    margin-bottom: 20px;
                }

                .consent-question h4 {
                    color: #2c3e50;
                    margin-bottom: 10px;
                }

                .consent-question p {
                    color: #666;
                    font-size: 14px;
                }

                .action-buttons {
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                }

                .consent-btn, .decline-btn {
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    border: none;
                    transition: all 0.3s ease;
                }

                .consent-btn {
                    background: linear-gradient(135deg, #2ecc71, #27ae60);
                    color: white;
                }

                .decline-btn {
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                }

                .consent-btn:hover, .decline-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                }
            `;
            document.head.appendChild(contentStyle);

            // Show content and hide loading
            loading.style.display = 'none';
            modalContent.style.display = 'block';

            // Bind event handlers with error checking
            const consentBtn = document.getElementById('modalConsentBtn');
            const declineBtn = document.getElementById('modalDeclineBtn');

            if (consentBtn && declineBtn) {
                consentBtn.onclick = () => this.submitFollowupConsent(followup.id, true);
                declineBtn.onclick = () => this.submitFollowupConsent(followup.id, false);
            } else {
                console.error('Consent buttons not found in rendered content');
                this.showModalError('Failed to initialize consent buttons. Please refresh the page.');
            }

        } catch (error) {
            console.error('Error rendering follow-up content:', error);
            this.showModalError('Failed to display follow-up details properly. Please try again.');
        }
    }

    submitFollowupConsent(followupRequestId, consentGiven) {
        const form = document.getElementById('consentForm');
        const buttons = document.querySelectorAll('.consent-btn, .decline-btn');

        // Set loading state
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Processing...';
        });

        // Set form value
        document.getElementById('consentInput').value = consentGiven;

        // Submit form
        const formData = new FormData(form);

        fetch(`/followup/${followupRequestId}/consent/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message and close modal
                this.showModalSuccess(consentGiven ? 'Acceptance given successfully!' : 'Follow-up declined successfully.');
                setTimeout(() => {
                    this.closeFollowupConsentModal();
                }, 2000);
            } else {
                this.showModalError(data.error || 'An error occurred while processing your response.');
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.innerHTML = btn.id === 'modalConsentBtn' ?
                        '<i class="bx bx-check"></i> Yes, I Accept' :
                        '<i class="bx bx-x"></i> No, Decline';
                });
            }
        })
        .catch(error => {
            console.error('Error submitting consent:', error);
            this.showModalError('An error occurred while processing your response.');
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.innerHTML = btn.id === 'modalConsentBtn' ?
                    '<i class="bx bx-check"></i> Yes, I Accept' :
                    '<i class="bx bx-x"></i> No, Decline';
            });
        });
    }

    showModalSuccess(message) {
        const modalBody = document.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="modal-message success">
                <i class="bx bx-check-circle"></i>
                <h4>Success</h4>
                <p>${message}</p>
            </div>
        `;
    }

    showModalError(message) {
        // Use the specific follow-up modal
        const modalBody = document.querySelector('#followup-consent-modal .modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="modal-message error">
                    <i class="bx bx-error-circle"></i>
                    <h4>Error</h4>
                    <p>${message}</p>
                </div>
            `;
        } else {
            // Fallback to any modal body
            const fallbackModalBody = document.querySelector('.modal-body');
            if (fallbackModalBody) {
                fallbackModalBody.innerHTML = `
                    <div class="modal-message error">
                        <i class="bx bx-error-circle"></i>
                        <h4>Error</h4>
                        <p>${message}</p>
                    </div>
                `;
            } else {
                // Last resort - show alert
                alert('Error: ' + message);
            }
        }
    }

    closeFollowupConsentModal() {
        const modal = document.getElementById('followup-consent-modal');
        if (modal) {
            modal.remove();
        }
    }

    showFollowupSchedulingModal(followupRequestId) {
        console.log('📅 Showing follow-up scheduling modal for request ID:', followupRequestId);

        // Remove any existing modal with the same ID
        const existingModal = document.getElementById('followup-scheduling-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal for follow-up scheduling
        const modal = document.createElement('div');
        modal.id = 'followup-scheduling-modal';
        modal.className = 'modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        `;
        modal.innerHTML = `
            <div class="modal-content followup-scheduling-modal" style="
                background: white;
                border-radius: 12px;
                max-width: 700px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            ">
                <div class="modal-header" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #eee;
                ">
                    <h3 style="margin: 0; color: #2c3e50;">Schedule Follow-up Session</h3>
                    <button class="modal-close" onclick="notificationManager.closeFollowupSchedulingModal()" style="
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <div class="loading-spinner" id="schedulingModalLoading" style="
                        text-align: center;
                        padding: 40px;
                    ">
                        <div class="spinner" style="
                            border: 4px solid #f3f3f3;
                            border-top: 4px solid #2ecc71;
                            border-radius: 50%;
                            width: 40px;
                            height: 40px;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 20px;
                        "></div>
                        <p>Loading scheduling form...</p>
                    </div>
                    <div id="schedulingModalContent" style="display: none;">
                        <!-- Content will be loaded here -->
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        console.log('Scheduling modal appended to body');

        // Load modal content
        this.loadFollowupSchedulingContent(followupRequestId);
    }

    loadFollowupSchedulingContent(followupRequestId) {
        console.log('Loading follow-up scheduling content for ID:', followupRequestId);

        // Create AbortController for timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
            console.log('Fetch request timed out');
            this.showModalError('Request timed out. Please check your connection and try again.');
        }, 10000); // 10 second timeout

        console.log('Starting fetch for scheduling form...');
        fetch(`/followup/${followupRequestId}/schedule/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            console.log('Fetch completed. Response status:', response.status, 'Response ok:', response.ok);

            if (!response.ok) {
                console.log('Response not ok, throwing error');
                return response.text().then(text => {
                    try {
                        const errorData = JSON.parse(text);
                        throw new Error(errorData.error || `HTTP ${response.status}`);
                    } catch (e) {
                        throw new Error(text || `HTTP ${response.status}`);
                    }
                });
            }

            console.log('Response is ok, getting text...');
            return response.text();
        })
        .then(html => {
            console.log('Received HTML content, length:', html.length);

            // Validate HTML content
            if (!html || html.length < 100) {
                throw new Error('Invalid response format - received empty or incomplete HTML');
            }

            // Show content and hide loading
            const modalContent = document.getElementById('schedulingModalContent');
            const loading = document.getElementById('schedulingModalLoading');

            if (!modalContent || !loading) {
                console.error('Modal elements not found');
                this.showModalError('Modal display error. Please refresh the page.');
                return;
            }

            modalContent.innerHTML = html;
            loading.style.display = 'none';
            modalContent.style.display = 'block';

            console.log('Scheduling form loaded successfully');

            // Add form submission handler
            const form = modalContent.querySelector('form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.submitFollowupScheduling(followupRequestId, form);
                });
            }

        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error loading follow-up scheduling modal:', error);
            console.error('Error message:', error.message);
            console.error('Error name:', error.name);

            // Handle different error types
            if (error.name === 'AbortError') {
                console.log('Request was aborted (timeout)');
                this.showModalError('Request timed out. Please check your connection and try again.');
            } else if (error.message && error.message.includes('404')) {
                this.showModalError('Follow-up request not found.');
            } else if (error.message && error.message.includes('403')) {
                this.showModalError('You do not have permission to schedule this follow-up.');
            } else if (error.message && error.message.includes('500')) {
                this.showModalError('Server error occurred. Please try again later.');
            } else {
                this.showModalError('Failed to load scheduling form. Please check your connection and try again.');
            }
        });
    }

    submitFollowupScheduling(followupRequestId, form) {
        console.log('Submitting follow-up scheduling form for request ID:', followupRequestId);

        const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
        const originalText = submitBtn ? submitBtn.value || submitBtn.textContent : 'Schedule Session';

        // Set loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.value = submitBtn.value ? 'Scheduling...' : 'Scheduling...';
            submitBtn.textContent = submitBtn.textContent ? 'Scheduling...' : 'Scheduling...';
        }

        // Get CSRF token
        const csrfToken = this.getCSRFToken();

        // Submit form
        const formData = new FormData(form);

        fetch(`/followup/${followupRequestId}/schedule/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => {
            console.log('Scheduling submission response status:', response.status);

            if (response.redirected) {
                // Handle redirect (success)
                console.log('Redirect detected, scheduling successful');
                this.showModalSuccess('Follow-up session scheduled successfully!');
                setTimeout(() => {
                    this.closeFollowupSchedulingModal();
                    // Optionally refresh the page or redirect
                    window.location.reload();
                }, 2000);
                return;
            }

            return response.text().then(text => {
                if (response.ok) {
                    // Success
                    console.log('Scheduling successful');
                    this.showModalSuccess('Follow-up session scheduled successfully!');
                    setTimeout(() => {
                        this.closeFollowupSchedulingModal();
                        // Optionally refresh the page or redirect
                        window.location.reload();
                    }, 2000);
                } else {
                    // Error
                    console.error('Scheduling failed:', text);
                    this.showModalError('Failed to schedule follow-up session. Please try again.');
                    // Re-enable submit button
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.value = submitBtn.value ? originalText : originalText;
                        submitBtn.textContent = submitBtn.textContent ? originalText : originalText;
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error submitting scheduling form:', error);
            this.showModalError('An error occurred while scheduling the session. Please try again.');
            // Re-enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.value = submitBtn.value ? originalText : originalText;
                submitBtn.textContent = submitBtn.textContent ? originalText : originalText;
            }
        });
    }

    closeFollowupSchedulingModal() {
        const modal = document.getElementById('followup-scheduling-modal');
        if (modal) {
            modal.remove();
        }
    }

    showScheduledFollowupModal(followupRequestId, metadata) {
        try {
            console.log('📅 Showing scheduled follow-up modal for request ID:', followupRequestId, 'with metadata:', metadata);

            // Remove any existing modal with the same ID
            const existingModal = document.getElementById('scheduled-followup-modal');
            console.log('📅 Existing modal found:', !!existingModal);
            if (existingModal) {
                existingModal.remove();
                console.log('📅 Removed existing modal');
            }

            // Create modal for scheduled follow-up details
            const modal = document.createElement('div');
            modal.id = 'scheduled-followup-modal';
            modal.className = 'modal-overlay';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            `;
            modal.innerHTML = `
                <div class="modal-content scheduled-followup-modal" style="
                    background: white;
                    border-radius: 12px;
                    max-width: 600px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                ">
                    <div class="modal-header" style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 20px;
                        border-bottom: 1px solid #eee;
                    ">
                        <h3 style="margin: 0; color: #2c3e50;">Scheduled Follow-up Session</h3>
                        <button class="modal-close" onclick="notificationManager.closeScheduledFollowupModal()" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #999;
                            padding: 0;
                            width: 30px;
                            height: 30px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">&times;</button>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
                        <div class="loading-spinner" id="scheduledModalLoading" style="
                            text-align: center;
                            padding: 40px;
                        ">
                            <div class="spinner" style="
                                border: 4px solid #f3f3f3;
                                border-top: 4px solid #2ecc71;
                                border-radius: 50%;
                                width: 40px;
                                height: 40px;
                                animation: spin 1s linear infinite;
                                margin: 0 auto 20px;
                            "></div>
                            <p>Loading session details...</p>
                        </div>
                        <div id="scheduledModalContent" style="display: none;">
                            <!-- Content will be loaded here -->
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            console.log('Scheduled follow-up modal appended to body');

            // Verify modal was added
            const addedModal = document.getElementById('scheduled-followup-modal');
            console.log('📅 Modal successfully added to DOM:', !!addedModal);

            // Load modal content
            this.loadScheduledFollowupContent(followupRequestId, metadata);
        } catch (error) {
            console.error('❌ Error in showScheduledFollowupModal:', error);
            this.showModalError('Failed to show scheduled follow-up modal. Please try again.');
        }
    }

    loadScheduledFollowupContent(followupRequestId, metadata) {
        console.log('Loading scheduled follow-up content for ID:', followupRequestId, 'with metadata:', metadata);

        // Create AbortController for timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
            console.log('Fetch request timed out');
            this.showModalError('Request timed out. Please check your connection and try again.');
        }, 10000); // 10 second timeout

        console.log('Starting fetch for scheduled follow-up details...');
        console.log('📡 Fetch URL:', `/followup/${followupRequestId}/details/`);
        fetch(`/followup/${followupRequestId}/details/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            console.log('📡 Fetch completed. Response status:', response.status, 'Response ok:', response.ok);

            if (!response.ok) {
                console.log('📡 Response not ok, throwing error');
                return response.text().then(text => {
                    console.log('📡 Error response text:', text);
                    try {
                        const errorData = JSON.parse(text);
                        throw new Error(errorData.error || `HTTP ${response.status}`);
                    } catch (e) {
                        throw new Error(text || `HTTP ${response.status}`);
                    }
                });
            }

            console.log('📡 Response is ok, parsing JSON...');
            return response.json();
        })
        .then(data => {
            console.log('Received JSON data:', data);

            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }

            if (data.success) {
                console.log('📡 Data success, rendering scheduled follow-up content...');
                console.log('📡 Data to render:', data);
                try {
                    this.renderScheduledFollowupContent(data, metadata);
                    console.log('📡 Scheduled follow-up content rendered successfully');
                } catch (error) {
                    console.error('📡 Error rendering scheduled follow-up content:', error);
                    this.showModalError('Failed to display session details. The data may be corrupted.');
                }
            } else {
                console.log('📡 Data not success, showing error:', data.error);
                // Handle specific error cases
                const errorMessage = data.error || 'Failed to load session details';
                if (errorMessage.includes('not available') || errorMessage.includes('not found')) {
                    this.showModalError('This follow-up session is no longer available. It may have been cancelled or completed.');
                } else if (errorMessage.includes('permission') || errorMessage.includes('denied')) {
                    this.showModalError('You do not have permission to view this follow-up session.');
                } else {
                    this.showModalError(errorMessage);
                }
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error loading scheduled follow-up modal:', error);
            console.error('Error message:', error.message);
            console.error('Error name:', error.name);

            // Handle different error types
            if (error.name === 'AbortError') {
                console.log('Request was aborted (timeout)');
                this.showModalError('Request timed out. Please check your connection and try again.');
            } else if (error.message && error.message.includes('404')) {
                this.showModalError('This follow-up session is no longer available.');
            } else if (error.message && error.message.includes('403')) {
                this.showModalError('You do not have permission to view this follow-up session.');
            } else if (error.message && error.message.includes('500')) {
                this.showModalError('Server error occurred. Please try again later.');
            } else if (error.message && error.message.includes('Invalid response format')) {
                this.showModalError('Received invalid data from server. Please refresh the page.');
            } else {
                this.showModalError('Failed to load session details. Please check your connection and try again.');
            }
        });
    }

    renderScheduledFollowupContent(data, metadata) {
        console.log('🎨 Rendering scheduled follow-up content with data:', data, 'metadata:', metadata);

        const modalContent = document.getElementById('scheduledModalContent');
        const loading = document.getElementById('scheduledModalLoading');

        if (!modalContent || !loading) {
            console.error('Modal elements not found');
            this.showModalError('Modal display error. Please refresh the page.');
            return;
        }

        try {
            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data structure received');
            }

            const followup = data.followup_request;
            const appointment = data.appointment;
            const counselor = data.counselor;
            const student = data.student;

            console.log('📊 Extracted data:', {
                followup: followup ? { id: followup.id, reason: followup.reason } : null,
                appointment: appointment ? { date: appointment.date, time: appointment.time, services: appointment.services } : null,
                counselor: counselor ? { name: counselor.name, unit: counselor.unit } : null,
                student: student ? { full_name: student.full_name, student_id: student.student_id } : null
            });

            // Validate required data
            if (!followup || !followup.id) {
                throw new Error('Follow-up request data is missing or invalid');
            }

            // Safe data extraction with fallbacks
            const studentName = (student && student.full_name) ? student.full_name : 'Unknown Student';
            const studentId = (student && student.student_id) ? student.student_id : 'N/A';
            const counselorName = (counselor && counselor.name) ? counselor.name : 'Unknown Counselor';
            const counselorUnit = (counselor && counselor.unit) ? counselor.unit : 'Unknown Unit';
            const counselorImage = (counselor && counselor.image_url) ? counselor.image_url : '/static/img/default.jpg';

            // Use API data for appointment details (formatted), fallback to metadata (raw)
            const appointmentDate = (appointment && appointment.date) || metadata.scheduled_date || 'TBD';
            const appointmentTime = (appointment && appointment.time) || metadata.scheduled_time || 'TBD';
            const appointmentType = (appointment && appointment.session_type) || metadata.session_type || 'TBD';
            const appointmentTypeRaw = (appointment && appointment.session_type_raw) || metadata.session_type || 'face_to_face';  // Use raw session type for video logic
            const services = (appointment && appointment.services) || metadata.services || ['Follow-up Session'];
            const videoUrl = appointment && appointment.video_call_url ? appointment.video_call_url : '#';
            const sessionDetailsUrl = appointment && appointment.id ? '/appointments/' + appointment.id + '/view/' : '#';

            // Format services
            const servicesText = Array.isArray(services) ? services.join(', ') : services;

            // Build video button HTML if applicable - use raw session type for accurate detection
            const videoButtonHtml = (appointmentTypeRaw && (appointmentTypeRaw.toLowerCase().includes('remote')) && videoUrl !== '#') ?
                '<button type="button" class="video-recording-btn" onclick="window.open(\'' + videoUrl + '\', \'_blank\');" style="' +
                    'padding: 12px 24px;' +
                    'border-radius: 8px;' +
                    'font-size: 14px;' +
                    'font-weight: 600;' +
                    'cursor: pointer;' +
                    'border: none;' +
                    'background: linear-gradient(135deg, #3498db, #2980b9);' +
                    'color: white;' +
                    'transition: all 0.3s ease;' +
                '" onmouseover="this.style.transform=\'translateY(-2px)\'; this.style.boxShadow=\'0 5px 15px rgba(52,152,219,0.3)\'" onmouseout="this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'none\'">' +
                    '<i class="bx bx-video"></i> View Video Recording' +
                '</button>' : '';

            console.log('📋 Final display data:', {
                studentName,
                studentId,
                counselorName,
                counselorUnit,
                appointmentDate,
                appointmentTime,
                appointmentType,
                servicesText,
                followupReason: followup.reason
            });

            // Check if this looks like test data
            const isTestData = studentName.includes('Test') || studentName.includes('test') ||
                              counselorName.includes('Test') || counselorName.includes('test') ||
                              followup.reason.includes('test') || followup.reason.includes('Test');

            if (isTestData) {
                console.warn('⚠️ WARNING: Modal appears to be showing test data!');
                console.warn('⚠️ Student name:', studentName);
                console.warn('⚠️ Counselor name:', counselorName);
                console.warn('⚠️ Followup reason:', followup.reason);
            } else {
                console.log('✅ Modal data appears to be real data');
            }

            const html = [];
            html.push('<div class="scheduled-followup-details">');

            // Session status
            html.push('<div class="session-status" style="background: rgba(46, 204, 113, 0.1); border-left: 4px solid #2ecc71; padding: 15px; margin-bottom: 20px; border-radius: 8px;">');
            html.push('<h4 style="margin: 0 0 10px 0; color: #27ae60; display: flex; align-items: center;">');
            html.push('<i class="bx bx-check-circle" style="margin-right: 8px;"></i>');
            html.push('Session Scheduled Successfully');
            html.push('</h4>');
            html.push('<p style="margin: 0; color: #2c3e50; font-size: 14px;">');
            html.push('This follow-up session has been scheduled and the student has been notified.');
            html.push('</p>');
            html.push('</div>');

            // Student info
            html.push('<div class="student-info" style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">');
            html.push('<div class="student-avatar" style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #3498db, #2980b9); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">');
            html.push(studentName.charAt(0).toUpperCase());
            html.push('</div>');
            html.push('<div class="student-details">');
            html.push('<h4 style="margin: 0 0 5px 0; color: #2c3e50;">');
            html.push(studentName);
            html.push('</h4>');
            html.push('<p style="margin: 0; color: #666; font-size: 14px;">Student ID: ');
            html.push(studentId);
            html.push('</p>');
            html.push('</div>');
            html.push('</div>');

            // Counselor info
            html.push('<div class="counselor-info" style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">');
            html.push('<img src="');
            html.push(counselorImage);
            html.push('" alt="');
            html.push(counselorName);
            html.push('" class="counselor-avatar" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #2ecc71;" onerror="this.src=\'/static/img/default.jpg\'">');
            html.push('<div class="counselor-details">');
            html.push('<h4 style="margin: 0 0 5px 0; color: #2c3e50;">');
            html.push(counselorName);
            html.push('</h4>');
            html.push('<p style="margin: 0; color: #666; font-size: 14px;">');
            html.push(counselorUnit);
            html.push('</p>');
            html.push('</div>');
            html.push('</div>');

            // Appointment details
            html.push('<div class="appointment-details" style="background: white; border: 1px solid #eee; border-radius: 8px; padding: 20px; margin-bottom: 20px;">');
            html.push('<h4 style="margin: 0 0 15px 0; color: #2c3e50; border-bottom: 2px solid #2ecc71; padding-bottom: 10px;">Appointment Details</h4>');
            html.push('<div class="detail-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">');

            html.push('<div class="detail-item">');
            html.push('<span class="detail-label" style="font-weight: 600; color: #555; display: block; margin-bottom: 5px;">Date:</span>');
            html.push('<span class="detail-value" style="font-weight: 600; color: #2c3e50; font-size: 16px;">');
            html.push(appointmentDate);
            html.push('</span>');
            html.push('</div>');

            html.push('<div class="detail-item">');
            html.push('<span class="detail-label" style="font-weight: 600; color: #555; display: block; margin-bottom: 5px;">Time:</span>');
            html.push('<span class="detail-value" style="font-weight: 600; color: #2c3e50; font-size: 16px;">');
            html.push(appointmentTime);
            html.push('</span>');
            html.push('</div>');

            html.push('<div class="detail-item">');
            html.push('<span class="detail-label" style="font-weight: 600; color: #555; display: block; margin-bottom: 5px;">Session Type:</span>');
            html.push('<span class="detail-value" style="font-weight: 600; color: #2c3e50;">');
            html.push(appointmentType);
            html.push('</span>');
            html.push('</div>');

            html.push('<div class="detail-item">');
            html.push('<span class="detail-label" style="font-weight: 600; color: #555; display: block; margin-bottom: 5px;">Services:</span>');
            html.push('<span class="detail-value" style="font-weight: 600; color: #2c3e50;">');
            html.push(servicesText);
            html.push('</span>');
            html.push('</div>');

            html.push('</div>');
            html.push('</div>');

            // Follow-up info
            html.push('<div class="followup-info" style="background: rgba(52, 152, 219, 0.1); border-left: 4px solid #3498db; padding: 15px; border-radius: 8px; margin-bottom: 20px;">');
            html.push('<h4 style="margin: 0 0 10px 0; color: #2980b9;">Follow-up Reason</h4>');
            html.push('<p style="margin: 0; color: #2c3e50; line-height: 1.5;">');
            html.push(followup.reason || 'Follow-up session as requested by counselor.');
            html.push('</p>');
            html.push('</div>');

            // Action buttons
            html.push('<div class="action-buttons" style="display: flex; justify-content: center; gap: 15px; margin-top: 20px; flex-wrap: wrap;">');

            // For counselor modals, the session details are already shown in the modal, so no need for the button

            if (videoButtonHtml) {
                html.push(videoButtonHtml);
            }

            html.push('<button type="button" class="close-btn" onclick="notificationManager.closeScheduledFollowupModal()" style="padding: 12px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; background: linear-gradient(135deg, #95a5a6, #7f8c8d); color: white; transition: all 0.3s ease;" onmouseover="this.style.transform=\'translateY(-2px)\'; this.style.boxShadow=\'0 5px 15px rgba(0,0,0,0.2)\'" onmouseout="this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'none\'">');
            html.push('<i class="bx bx-x"></i> Close');
            html.push('</button>');

            html.push('</div>');
            html.push('</div>');

            modalContent.innerHTML = html.join('');

            // Show content and hide loading
            loading.style.display = 'none';
            modalContent.style.display = 'block';

        } catch (error) {
            console.error('Error rendering scheduled follow-up content:', error);
            this.showModalError('Failed to display session details properly. Please try again.');
        }
    }

    closeScheduledFollowupModal() {
        const modal = document.getElementById('scheduled-followup-modal');
        if (modal) {
            modal.remove();
        }
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    showToast(notification) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${notification.priority || 'normal'}`;
        toast.dataset.notificationId = notification.id;

        const icon = this.getNotificationIcon(notification.type);
        const timeAgo = this.getTimeAgo(new Date(notification.created_at));

        // Extract followup_request_id from metadata for follow-up notifications
        let metadata = notification.metadata || {};
        if (typeof metadata === 'string') {
            try {
                metadata = JSON.parse(metadata);
            } catch (e) {
                console.warn('Failed to parse notification metadata:', e);
                metadata = {};
            }
        }
        const followupRequestId = metadata.followup_request_id;
        console.log('Toast creation - notification metadata:', metadata, 'followupRequestId:', followupRequestId);
        console.log('Toast creation - notification ID:', notification.id, 'type:', notification.type);

        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-title">
                    <i class="bx ${icon} toast-icon"></i>
                    ${this.getNotificationTitle(notification.type)}
                </div>
                <button class="toast-close" onclick="notificationManager.closeToast(this)">&times;</button>
            </div>
            <div class="toast-message">${notification.message}</div>
            ${notification.url && notification.url !== '#' ? `
                <div class="toast-actions">
                    <button class="toast-action" data-notification-id="${notification.id}" data-type="${notification.type}" data-action-text="${notification.action_text ? notification.action_text.replace(/"/g, '"') : ''}" data-action-url="${notification.url}" data-followup-request-id="${followupRequestId || ''}">
                        ${notification.action_text || 'View'}
                    </button>
                </div>
            ` : ''}
            <div class="toast-time">${timeAgo}</div>
        `;

        // Add event listener to the action button
        const actionButton = toast.querySelector('.toast-action');
        if (actionButton) {
            actionButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const type = actionButton.dataset.type;
                const actionText = actionButton.dataset.actionText;
                const actionUrl = actionButton.dataset.actionUrl;
                const notificationId = parseInt(actionButton.dataset.notificationId);
                const followupRequestId = actionButton.dataset['followup-request-id'];
                console.log('Toast action clicked - type:', type, 'followupRequestId:', followupRequestId, 'metadata to pass:', metadata);
                this.handleNotificationAction(type, actionText, actionUrl, notificationId, followupRequestId, metadata);
            });
        }

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
                // Don't navigate, let the in-app notification handle it
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
        this.ensureConnection();
        // Wait a bit for connection to establish, then send
        setTimeout(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'mark_read',
                    notification_id: notificationId
                }));
            }
        }, 500);
    }

    markAllAsRead() {
        this.ensureConnection();
        // Wait a bit for connection to establish, then send
        setTimeout(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'mark_all_read'
                }));
            }
        }, 500);
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
    
    setupLazyConnection() {
        // Connect WebSocket after user interaction to avoid Railway cold starts
        const connectTriggers = [
            // Connect after 10 seconds of inactivity (user is engaged)
            () => setTimeout(() => this.ensureConnection(), 10000),

            // Connect immediately on any user interaction
            () => {
                let connected = false;
                const connectOnce = () => {
                    if (!connected) {
                        connected = true;
                        this.ensureConnection();
                    }
                };

                // Mouse/touch events
                document.addEventListener('click', connectOnce, { once: true });
                document.addEventListener('touchstart', connectOnce, { once: true });
                document.addEventListener('mousemove', connectOnce, { once: true });
                document.addEventListener('keydown', connectOnce, { once: true });
                document.addEventListener('scroll', connectOnce, { once: true });
            }
        ];

        // Execute all connection triggers
        connectTriggers.forEach(trigger => trigger());
    }

    ensureConnection() {
        if (!this.isConnected && !this.socket) {
            console.log('🔌 Lazy connecting to WebSocket...');
            this.connectWebSocket();
        }
    }

    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.unreadCount > 0) {
                // User returned to page, refresh notifications
                this.loadNotifications();
                // Also ensure WebSocket connection
                this.ensureConnection();
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
        this.ensureConnection();
        // Wait for connection to establish, then send
        setTimeout(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'test_notification'
                }));
            }
        }, 500);
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

// Initialize notification manager immediately
let notificationManager;

// Function to safely initialize notification manager
function initializeNotificationManager() {
    // Only initialize if not already done and user is authenticated
    if (!notificationManager && document.body && document.body.dataset.userAuthenticated !== 'false') {
        notificationManager = new NotificationManager();
        window.notificationManager = notificationManager;
        console.log('🔔 Notification manager initialized successfully');
        console.log('🔍 showScheduledFollowupModal method exists:', typeof window.notificationManager.showScheduledFollowupModal);
        return true;
    }
    return false;
}

// Try to initialize immediately if DOM is ready
if (document.readyState === 'loading') {
    // DOM not ready yet, wait for it
    document.addEventListener('DOMContentLoaded', function() {
        const initialized = initializeNotificationManager();
        if (!initialized) {
            console.log('🔔 Notification manager not initialized (user not authenticated or already initialized)');
        }
    });
} else {
    // DOM already ready
    initializeNotificationManager();
}

// Also try on window load as final fallback
window.addEventListener('load', function() {
    if (!notificationManager) {
        console.log('🔔 Attempting late initialization of notification manager');
        initializeNotificationManager();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}