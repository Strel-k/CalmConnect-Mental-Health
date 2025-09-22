# CalmConnect Real-time Notification System

## Overview

The CalmConnect notification system has been completely modernized with real-time WebSocket capabilities, enhanced categorization, priority levels, and a centralized service architecture.

## 🚀 Key Features

### Real-time Capabilities
- **WebSocket Integration**: Instant notification delivery via WebSocket connections
- **Live Updates**: Real-time notification count and status updates
- **Auto-reconnection**: Automatic reconnection with exponential backoff
- **Connection Monitoring**: Visual connection status indicators

### Enhanced Notification Types
- **Priority Levels**: Low, Normal, High, Urgent
- **Categories**: Appointment, Report, System, Reminder, Feedback, General
- **Interactive Notifications**: Action buttons for quick responses
- **Expiring Notifications**: Automatic cleanup of expired notifications

### Modern User Experience
- **Toast Notifications**: Animated slide-in notifications
- **Browser Notifications**: Native browser notification support
- **Sound Alerts**: Audio feedback for urgent notifications
- **Visual Indicators**: Color-coded notifications by priority

## 📁 File Structure

```
mentalhealth/
├── models.py                           # Enhanced Notification model
├── consumers.py                        # WebSocket consumers (NotificationConsumer)
├── routing.py                          # WebSocket URL routing
├── notification_service.py             # Centralized notification service
├── views.py                            # Updated notification views
├── migrations/
│   └── 0023_enhance_notifications.py   # Database migration
├── static/mentalhealth/js/
│   └── notifications.js                # Frontend notification manager
└── templates/mentalhealth/
    ├── base_notifications.html         # Notification system template
    └── notification_demo.html          # Demo page
```

## 🔧 Technical Implementation

### Backend Components

#### 1. Enhanced Notification Model (`models.py`)
```python
class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('appointment', 'Appointment'),
        ('report', 'Report'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
        ('feedback', 'Feedback'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    url = models.URLField(blank=True, null=True)
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
```

#### 2. WebSocket Consumer (`consumers.py`)
```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        self.user = self.scope["user"]
        self.group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        # Send current notification count
        await self.send_notification_count()
```

#### 3. Notification Service (`notification_service.py`)
```python
class NotificationService:
    def create_notification(self, user, message, notification_type='general', 
                          priority='normal', category=None, action_url=None, 
                          action_text=None, expires_in_hours=None, metadata=None):
        # Create notification and send via WebSocket
        
    def create_appointment_notification(self, appointment, action):
        # Specialized appointment notifications
        
    def create_report_notification(self, report):
        # Specialized report notifications
```

### Frontend Components

#### 1. Notification Manager (`notifications.js`)
- **WebSocket Management**: Connection, reconnection, message handling
- **Toast Notifications**: Animated notification display
- **Browser Integration**: Native browser notifications
- **Audio Feedback**: Sound alerts for different priorities

#### 2. Enhanced UI (`base_notifications.html`)
- **Modern Dropdown**: Styled notification dropdown with actions
- **Real-time Updates**: Live count and status updates
- **Interactive Elements**: Mark as read, clear, action buttons

## 🎯 Usage Examples

### Creating Notifications

#### Using the Notification Service
```python
from .notification_service import notification_service

# Create appointment notification
notification_service.create_appointment_notification(appointment, 'created')

# Create custom notification
notification_service.create_notification(
    user=user,
    message="Your report is ready for review",
    notification_type='report',
    priority='high',
    action_url='/reports/123/',
    action_text='View Report',
    expires_in_hours=24
)
```

#### Legacy Support
```python
# Old method still works (backward compatible)
create_notification(
    user=user,
    message="Legacy notification",
    notification_type='general',
    url='/some-url/'
)
```

### Frontend Integration

#### Include in Templates
```html
<!-- Include the notification system -->
{% include 'mentalhealth/base_notifications.html' %}

<!-- Notification bell (existing bell icons will be enhanced automatically) -->
<button id="bell-icon">
    <i class="bx bx-bell"></i>
    <span class="notification-badge" id="notificationBadge"></span>
</button>
<div class="notification-dropdown" id="notificationDropdown"></div>
```

#### JavaScript API
```javascript
// Access the notification manager
window.notificationManager.markAsRead(notificationId);
window.notificationManager.markAllAsRead();
window.notificationManager.sendTestNotification();
```

## 🔄 WebSocket Message Types

### Client → Server
```json
{
    "type": "mark_read",
    "notification_id": 123
}

{
    "type": "mark_all_read"
}

{
    "type": "test_notification"
}
```

### Server → Client
```json
{
    "type": "new_notification",
    "notification": {
        "id": 123,
        "message": "Your appointment has been confirmed",
        "type": "appointment",
        "priority": "normal",
        "action_url": "/appointments/123/",
        "created_at": "2024-01-15T10:30:00Z"
    }
}

{
    "type": "notification_count",
    "count": 5
}
```

## 🛠️ Installation & Setup

### 1. Database Migration
```bash
cd calmconnect_backend
py manage.py migrate mentalhealth
```

### 2. WebSocket Configuration
Ensure your `settings.py` includes:
```python
INSTALLED_APPS = [
    # ... other apps
    'channels',
    'mentalhealth',
]

ASGI_APPLICATION = 'calmconnect_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### 3. URL Configuration
The notification URLs are automatically included in `mentalhealth/urls.py`:
- `/notifications/` - Get notifications API
- `/notifications/<id>/clear/` - Clear specific notification
- `/notifications/clear-all/` - Clear all notifications
- `/notification-demo/` - Demo page

### 4. WebSocket Routing
WebSocket endpoint: `ws://localhost:8000/ws/notifications/`

## 🧪 Testing

### Demo Page
Visit `/notification-demo/` to test the real-time notification system:
- Test different notification types and priorities
- Monitor WebSocket connection status
- View activity logs
- Test browser notifications

### Manual Testing
```python
# In Django shell
from mentalhealth.notification_service import notification_service
from mentalhealth.models import CustomUser

user = CustomUser.objects.first()
notification_service.create_notification(
    user=user,
    message="Test notification",
    priority='urgent',
    notification_type='system'
)
```

## 📊 Performance Considerations

### Database Optimization
- **Indexes**: Added on user_id, created_at, read, dismissed
- **Cleanup**: Automatic removal of expired notifications
- **Pagination**: Limited to 20 recent notifications per request

### WebSocket Optimization
- **User Groups**: Notifications sent only to relevant users
- **Connection Pooling**: Efficient connection management
- **Reconnection Logic**: Exponential backoff for failed connections

### Frontend Optimization
- **Lazy Loading**: Notifications loaded on demand
- **Caching**: Browser caching for static assets
- **Debouncing**: Prevents excessive API calls

## 🔒 Security Features

### Authentication
- **User Verification**: WebSocket connections require authentication
- **CSRF Protection**: All HTTP requests include CSRF tokens
- **Permission Checks**: Users can only access their own notifications

### Data Protection
- **Input Sanitization**: All notification content is sanitized
- **XSS Prevention**: HTML content is properly escaped
- **Rate Limiting**: Protection against notification spam

## 🎨 Customization

### Styling
Customize notification appearance by modifying the CSS in `base_notifications.html`:
```css
.toast.urgent {
    border-left-color: #dc3545;
    background: #fff5f5;
}
```

### Notification Types
Add new notification types by updating:
1. `CATEGORY_CHOICES` in `models.py`
2. Icon mapping in `notifications.js`
3. Color schemes in CSS

### Sound Alerts
Customize notification sounds in `notifications.js`:
```javascript
playNotificationSound(priority) {
    const frequency = priority === 'urgent' ? 800 : 600;
    // ... audio generation code
}
```

## 🐛 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
- Check if Django Channels is properly configured
- Verify ASGI application is set correctly
- Ensure WebSocket URL is accessible

#### Notifications Not Appearing
- Check user authentication status
- Verify notification permissions in browser
- Check browser console for JavaScript errors

#### Migration Errors
- Ensure all previous migrations are applied
- Check for conflicting migration files
- Run `py manage.py showmigrations` to verify status

### Debug Mode
Enable debug logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mentalhealth.consumers': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🔮 Future Enhancements

### Planned Features
- **Push Notifications**: Mobile app integration
- **Email Digests**: Daily/weekly notification summaries
- **Smart Filtering**: AI-powered notification prioritization
- **Bulk Operations**: Advanced notification management
- **Analytics**: Notification engagement tracking

### Integration Opportunities
- **Calendar Integration**: Sync with external calendars
- **SMS Notifications**: Text message alerts for urgent notifications
- **Slack Integration**: Team notification channels
- **Mobile App**: React Native notification support

## 📈 Monitoring & Analytics

### Metrics to Track
- Notification delivery rate
- User engagement (read/click rates)
- WebSocket connection stability
- Average response time

### Health Checks
- WebSocket endpoint availability
- Database query performance
- Notification queue length
- Error rates

## 🤝 Contributing

When adding new notification features:
1. Update the `Notification` model if needed
2. Add new notification types to the service
3. Update frontend JavaScript for new UI elements
4. Add appropriate tests
5. Update this documentation

## 📞 Support

For issues with the notification system:
1. Check the demo page at `/notification-demo/`
2. Review browser console for errors
3. Check Django logs for backend issues
4. Verify WebSocket connection status

---

**Last Updated**: January 2024  
**Version**: 2.0.0  
**Compatibility**: Django 4.x, Channels 4.x