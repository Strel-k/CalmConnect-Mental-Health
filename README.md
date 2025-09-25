# CalmConnect Backend

A Django-based mental health application with PostgreSQL database support.

## 🚀 Quick Start

### 1. Environment Setup
- Copy `.env.example` to `.env` and update the values:
  ```bash
  cp .env.example .env
  ```
- Edit `.env` with your actual database credentials and API keys

### 2. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL (if not installed)
# Create database and user
createdb calmconnect_db
createuser -P postgres_user

# Update .env file with your credentials
```

### 3. Install Dependencies
```bash
pip install -r requirements_fixed.txt
```

### 4. Run Migrations
```bash
python migrate_to_postgres.py
```

### 5. Start Development Server
```bash
python manage.py runserver
```

## 📁 Project Structure

```
calmconnect_backend/
├── mentalhealth/          # Main application
├── calmconnect_backend/   # Project settings
├── templates/            # HTML templates
├── static/               # Static files
├── media/                # User uploads
├── logs/                 # Application logs
├── .env                  # Environment variables
├── requirements_fixed.txt # Python dependencies
└── manage.py            # Django management script
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DB_NAME=calmconnect_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (optional)
OPENAI_API_KEY=your-openai-key

# Email
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
EMAIL_PORT=2525
```

## 🗄️ Database Migration

To migrate from SQLite to PostgreSQL:

1. Set up PostgreSQL database
2. Update `.env` with PostgreSQL credentials
3. Run: `python migrate_to_postgres.py`
4. Test: `python manage.py runserver`

## 🔒 Security Features

- Django Security Middleware
- CSRF protection
- XSS protection
- SQL injection prevention
- Rate limiting
- Secure session management
- Content Security Policy (CSP)

## 📊 Features

- User authentication and authorization
- Mental health assessments (DASS21)
- AI-powered feedback (OpenAI integration)
- Secure file uploads
- Email notifications
- Real-time WebSocket support
- Comprehensive logging

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Access admin panel
# Visit: http://localhost:8000/admin/
```

## 📝 Development Notes

- The application uses Django 4.2.x for stability
- PostgreSQL is configured as the primary database
- Environment variables are loaded using python-decouple
- Security headers are configured for production
- Logging is set up for monitoring and debugging

## 🚨 Production Deployment

1. Set `DJANGO_DEBUG=False` in `.env`
2. Generate a secure `DJANGO_SECRET_KEY`
3. Configure production database credentials
4. Set up proper email service
5. Configure static files serving
6. Set up SSL/HTTPS
7. Configure allowed hosts
8. Set up monitoring and logging

## 📞 Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review Django error messages
3. Verify environment variable configuration
4. Check database connectivity
