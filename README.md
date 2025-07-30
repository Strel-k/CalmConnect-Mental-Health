# CalmConnect - Mental Health Counseling Platform

A comprehensive web-based mental health counseling platform built with Django, featuring real-time video sessions, appointment scheduling, and AI-powered feedback.

## 🚀 Features

### Core Features
- **User Authentication & Profiles**: Student and counselor registration with email verification
- **Appointment Scheduling**: Interactive calendar-based scheduling system
- **Real-time Video Sessions**: WebRTC-powered video calls with chat functionality
- **DASS-21 Assessment**: Depression, Anxiety, and Stress Scale evaluation
- **AI-Powered Feedback**: OpenAI integration for personalized mental health insights
- **Counselor Management**: Admin panel for counselor oversight and scheduling
- **Session Recording**: Video call recording capabilities
- **Chat & Messaging**: Real-time messaging during sessions

### Technical Features
- **WebSocket Integration**: Real-time communication using Django Channels
- **WebRTC Video Calls**: Peer-to-peer video conferencing
- **Responsive Design**: Mobile-friendly interface
- **Email Notifications**: Automated appointment confirmations and reminders
- **File Upload**: Profile pictures and document management
- **Admin Dashboard**: Comprehensive analytics and management tools

## 🛠️ Technology Stack

- **Backend**: Django 5.1.3, Django Channels, ASGI
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Real-time**: WebSocket, WebRTC
- **AI Integration**: OpenAI API
- **Email**: SMTP with Django email backend
- **Authentication**: Django's built-in authentication system

## 📋 Prerequisites

- Python 3.8+
- pip
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd calmconnect_backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:
```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587

# OpenAI API (for AI feedback feature)
OPENAI_API_KEY=your-openai-api-key

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/calmconnect
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
```

## 🏃‍♂️ Running the Application

### Development Server (with WebSocket support)
```bash
# Using Daphne (recommended for WebSocket)
daphne calmconnect_backend.asgi:application

# Using Uvicorn
uvicorn calmconnect_backend.asgi:application

# Using Django's runserver (if configured for ASGI)
python manage.py runserver
```

### Production Server
```bash
# Using Daphne with multiple workers
daphne -b 0.0.0.0 -p 8000 calmconnect_backend.asgi:application

# Using Gunicorn with Daphne
gunicorn calmconnect_backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
```

## 🎯 Usage

### For Students
1. Register an account and verify your email
2. Complete the DASS-21 assessment
3. Browse available counselors and schedule appointments
4. Join video sessions at the scheduled time
5. Receive AI-powered feedback after sessions

### For Counselors
1. Register as a counselor and complete profile setup
2. Set your availability schedule
3. Accept appointment requests
4. Conduct video sessions with students
5. Create session reports and notes

### For Administrators
1. Access the admin dashboard at `/admin/`
2. Manage counselors and appointments
3. View analytics and reports
4. Monitor system health

## 🔧 Configuration

### WebSocket Configuration
The application uses Django Channels for real-time communication. Ensure your `settings.py` includes:
```python
INSTALLED_APPS = [
    # ...
    'channels',
    # ...
]

ASGI_APPLICATION = 'calmconnect_backend.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### Video Call Configuration
WebRTC video calls are configured with STUN servers for NAT traversal. For production, consider adding TURN servers:
```javascript
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
        // Add TURN servers for production
    ]
};
```

## 🐛 Troubleshooting

### Common Issues

#### Video Call Not Connecting
1. **Check browser permissions**: Ensure camera/microphone access is granted
2. **Verify WebSocket connection**: Check browser console for WebSocket errors
3. **Check signaling logs**: Look for offer/answer exchange in console
4. **Network issues**: STUN servers may not work on restricted networks

#### WebSocket Connection Issues
1. **Server not running with ASGI**: Use Daphne or Uvicorn, not WSGI
2. **Channel layer configuration**: Ensure Redis or InMemoryChannelLayer is configured
3. **CORS issues**: Check if WebSocket URL is accessible

#### Database Issues
1. **Migration errors**: Run `python manage.py makemigrations` and `python manage.py migrate`
2. **Permission errors**: Ensure database file is writable

### Debug Mode
Enable debug logging by setting `DJANGO_DEBUG=True` in your `.env` file.

## 📁 Project Structure

```
calmconnect_backend/
├── calmconnect_backend/     # Django project settings
├── mentalhealth/           # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # HTTP views and API endpoints
│   ├── consumers.py       # WebSocket consumers
│   ├── templates/         # HTML templates
│   └── static/           # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── staticfiles/          # Collected static files
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the troubleshooting section above

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with external mental health services
- [ ] Multi-language support
- [ ] Advanced AI features
- [ ] Payment processing integration
- [ ] Group therapy sessions
- [ ] Crisis intervention tools

---

**Note**: This is a development version. For production deployment, ensure all security measures are properly configured and sensitive data is protected. 