# CalmConnect Deployment Guide

## 🚀 Production Deployment

### 1. Environment Setup

Create a `.env` file in your project root (or set environment variables directly):

```bash
# Django Settings
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# OpenAI Integration
OPENAI_API_KEY=your-openai-api-key-here

# Email Configuration
EMAIL_HOST_USER=your-email-username
EMAIL_HOST_PASSWORD=your-email-password

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/calmconnect
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

For development (current setup):
```bash
python manage.py migrate
```

For production (recommended):
- Use PostgreSQL instead of SQLite
- Set up database backups
- Configure connection pooling

### 4. Static Files

```bash
python manage.py collectstatic
```

### 5. Security Checklist

✅ **Environment Variables**: All secrets moved to environment variables
✅ **HTTPS**: SSL certificate configured
✅ **Rate Limiting**: django-ratelimit installed and configured
✅ **Security Headers**: Django security middleware enabled
✅ **Access Control**: Student-only AI feedback endpoint
✅ **Data Sanitization**: PII removed from AI prompts
✅ **Logging**: Comprehensive audit trail implemented

### 6. Testing Security

Test the following scenarios:

```bash
# Test student access to AI feedback
curl -X POST https://your-domain.com/api/ai-feedback/ \
  -H "Authorization: Bearer <student-token>" \
  -H "Content-Type: application/json" \
  -d '{"depression": 5, "anxiety": 3, "stress": 4}'

# Test counselor access (should be denied)
curl -X POST https://your-domain.com/api/ai-feedback/ \
  -H "Authorization: Bearer <counselor-token>" \
  -H "Content-Type: application/json" \
  -d '{"depression": 5, "anxiety": 3, "stress": 4}'

# Test rate limiting
# Make multiple rapid requests - should get rate limited after 5 requests/minute
```

### 7. Monitoring Setup

#### Log Monitoring
- Monitor Django logs for security events
- Set up alerts for rate limit violations
- Track API usage patterns

#### Health Checks
```bash
# Check if Django is running
curl https://your-domain.com/health/

# Check security headers
curl -I https://your-domain.com/
```

### 8. Backup Strategy

#### Database Backups
```bash
# Daily automated backup
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Encrypt backups
gpg --encrypt backup_$(date +%Y%m%d).json
```

#### File Backups
- Backup media files
- Backup static files
- Backup configuration files

### 9. SSL Certificate

For production, ensure you have a valid SSL certificate:

```bash
# Using Let's Encrypt (example)
sudo certbot --nginx -d your-domain.com
```

### 10. Performance Optimization

#### Database
- Enable database connection pooling
- Set up database indexes
- Configure query optimization

#### Caching
- Set up Redis for session storage
- Configure Django caching
- Enable static file caching

### 11. Privacy Policy Updates

Ensure your privacy policy includes:

1. **AI/ML Usage Disclosure**
   - Clear explanation of OpenAI integration
   - Data anonymization practices
   - User consent requirements

2. **Data Retention**
   - How long DASS21 data is stored
   - Data deletion procedures
   - User rights and requests

3. **Third-Party Services**
   - OpenAI API usage
   - Email service providers
   - Analytics tools (if any)

### 12. Compliance Considerations

#### Educational Institutions
- FERPA compliance for student data
- Data retention policies
- Access control requirements

#### Healthcare (if applicable)
- HIPAA compliance considerations
- Data encryption requirements
- Audit trail requirements

### 13. Maintenance Schedule

#### Daily
- Monitor error logs
- Check system health
- Review security alerts

#### Weekly
- Review access logs
- Update dependencies
- Backup verification

#### Monthly
- Security assessment
- Performance review
- Privacy policy review

### 14. Emergency Procedures

#### System Down
1. Check server status
2. Review recent changes
3. Rollback if necessary
4. Notify users

#### Security Incident
1. Isolate affected systems
2. Preserve evidence
3. Notify authorities
4. Communicate with users

---

## 🔧 Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| DEBUG | True | False |
| ALLOWED_HOSTS | localhost | your-domain.com |
| SECURE_SSL_REDIRECT | False | True |
| Rate Limiting | Disabled | Enabled |
| Logging | Basic | Comprehensive |

---

**Next Steps**:
1. Set up your environment variables
2. Test the deployment locally
3. Deploy to your production server
4. Run security tests
5. Monitor system health

For questions or issues, refer to `SECURITY.md` for detailed security documentation. 