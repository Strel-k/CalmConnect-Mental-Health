# CalmConnect Security Documentation

## Overview
This document outlines the comprehensive security measures implemented for the CalmConnect mental health platform, with particular focus on protecting sensitive DASS21 assessment data and AI-powered feedback integration.

## 🔒 Security Measures Implemented

### 1. DASS21 Data Protection

#### Backend Security
- **Student-Only Access**: `/api/ai-feedback/` endpoint restricted to authenticated students only
- **Rate Limiting**: 5 requests per minute per user to prevent abuse
- **Input Validation**: Strict validation of all DASS21 scores (type checking, presence validation)
- **Data Sanitization**: All PII (names, emails, student IDs) removed from OpenAI prompts
- **Comprehensive Logging**: Access, errors, and suspicious activity logged (without sensitive data)

#### Data Flow Security
- **Anonymized Prompts**: Only non-identifiable info sent to OpenAI (age, year, program, college)
- **Secure Transport**: HTTPS enforcement ensures encrypted data transmission
- **Error Handling**: Generic error responses prevent sensitive data exposure

### 2. Production Security Settings

#### HTTPS & Transport Security
```python
SECURE_SSL_REDIRECT = not DEBUG  # Force HTTPS in production
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 3600 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

#### Environment Variables
All sensitive configuration moved to environment variables:
- `OPENAI_API_KEY`
- `DJANGO_SECRET_KEY`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

### 3. Access Control

#### Role-Based Access
- **Students**: Can access AI feedback, DASS21 tests, appointment booking
- **Counselors**: Can access reports, appointments, student data (with proper permissions)
- **Admins**: Can access all system functions and analytics

#### Authentication & Authorization
- All sensitive endpoints protected with `@login_required`
- Student-specific endpoints protected with `@student_required`
- Counselor-specific endpoints protected with `@counselor_required`
- Admin endpoints protected with `@staff_member_required`

### 4. AI Integration Security

#### OpenAI Integration
- **API Key Security**: Stored in environment variables, not in code
- **Data Minimization**: Only necessary DASS21 scores and anonymized profile data sent
- **Error Handling**: Secure error responses without exposing internal details
- **Rate Limiting**: Prevents API abuse and cost overruns

#### Privacy Compliance
- **No PII in AI Prompts**: Names, emails, student IDs completely excluded
- **Consent Required**: Users must consent before DASS21 tests
- **Transparency**: Clear disclosure of AI usage in privacy policy

## 🚀 Production Deployment Checklist

### Environment Setup
```bash
# Required environment variables
export OPENAI_API_KEY="your-openai-key"
export DJANGO_SECRET_KEY="your-secure-secret-key"
export EMAIL_HOST_USER="your-email-user"
export EMAIL_HOST_PASSWORD="your-email-password"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Security Headers
The application automatically sets security headers in production:
- HSTS (HTTP Strict Transport Security)
- XSS Protection
- Content Type Sniffing Prevention
- Frame Options (Clickjacking Protection)

### Database Security
- SQLite for development (consider PostgreSQL for production)
- Database not publicly accessible
- Regular backups with encryption
- Least-privilege access principles

## 📋 Privacy Policy Requirements

### AI/ML Disclosure
Your privacy policy should include:
- Clear disclosure of OpenAI usage for feedback
- Explanation that data sent to OpenAI is anonymized
- User consent requirements for DASS21 tests
- Data retention and deletion policies

### Consent Language
Example consent text:
> "By taking this DASS21 assessment, you consent to the use of AI-powered analysis to provide personalized feedback. Your responses will be anonymized before being processed by OpenAI's AI systems. No personally identifiable information will be shared with third parties."

## 🔍 Monitoring & Auditing

### Logging
- All API access logged (without sensitive data)
- Error conditions logged for debugging
- Suspicious activity flagged
- Rate limit violations tracked

### Regular Security Reviews
- Monthly security assessments
- Dependency vulnerability scanning
- Access log reviews
- Privacy policy updates

## 🛡️ Incident Response

### Data Breach Procedures
1. **Immediate Response**
   - Isolate affected systems
   - Preserve evidence
   - Notify relevant authorities

2. **User Notification**
   - Transparent communication
   - Clear explanation of impact
   - Remediation steps

3. **System Recovery**
   - Security audit
   - Vulnerability remediation
   - Enhanced monitoring

## 📞 Security Contacts

For security issues or questions:
- **Technical Issues**: Review logs and error reports
- **Privacy Concerns**: Update privacy policy and consent mechanisms
- **Compliance**: Ensure HIPAA/FERPA compliance for educational institutions

## 🔄 Maintenance

### Regular Updates
- Keep Django and dependencies updated
- Monitor security advisories
- Regular security testing
- Privacy policy reviews

### Backup Procedures
- Daily database backups
- Encrypted backup storage
- Regular backup testing
- Disaster recovery planning

---

**Last Updated**: [Current Date]
**Version**: 1.0
**Next Review**: [Date + 6 months] 