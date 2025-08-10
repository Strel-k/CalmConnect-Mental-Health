"""
Security check management command for CalmConnect
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from mentalhealth.models import Counselor, Appointment, DASSResult
import logging

User = get_user_model()

class Command(BaseCommand):
    help = 'Run security checks and display system health status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix security issues automatically',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('CalmConnect Security Check'))
        self.stdout.write('=' * 50)
        
        issues = []
        
        # Check environment variables
        issues.extend(self.check_environment_variables())
        
        # Check Django settings
        issues.extend(self.check_django_settings())
        
        # Check database security
        issues.extend(self.check_database_security())
        
        # Check file permissions
        issues.extend(self.check_file_permissions())
        
        # Check user accounts
        issues.extend(self.check_user_accounts())
        
        # Check logging
        issues.extend(self.check_logging())
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        if issues:
            self.stdout.write(
                self.style.ERROR(f'Found {len(issues)} security issues:')
            )
            for issue in issues:
                self.stdout.write(f'  - {issue}')
            
            if options['fix']:
                self.stdout.write('\nAttempting to fix issues...')
                self.fix_issues(issues, options)
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All security checks passed!')
            )
    
    def check_environment_variables(self):
        """Check critical environment variables"""
        issues = []
        
        # Check SECRET_KEY
        if not os.environ.get('DJANGO_SECRET_KEY'):
            issues.append('DJANGO_SECRET_KEY environment variable not set')
        
        # Check DEBUG setting
        if os.environ.get('DJANGO_DEBUG', 'True') == 'True' and not settings.DEBUG:
            issues.append('DEBUG should be False in production')
        
        # Check OpenAI API key
        if not os.environ.get('OPENAI_API_KEY'):
            issues.append('OPENAI_API_KEY not configured (AI feedback will use fallback)')
        
        # Check email settings
        if not os.environ.get('EMAIL_HOST_USER'):
            issues.append('EMAIL_HOST_USER not configured')
        
        self.stdout.write('Environment Variables: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def check_django_settings(self):
        """Check Django security settings"""
        issues = []
        
        # Check ALLOWED_HOSTS
        if settings.DEBUG and 'localhost' not in settings.ALLOWED_HOSTS:
            issues.append('localhost not in ALLOWED_HOSTS')
        
        # Check security headers
        if settings.DEBUG:
            if not getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False):
                issues.append('SECURE_BROWSER_XSS_FILTER should be True')
        
        # Check session security
        if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
            issues.append('SESSION_COOKIE_HTTPONLY should be True')
        
        # Check CSRF security
        if not getattr(settings, 'CSRF_COOKIE_HTTPONLY', False):
            issues.append('CSRF_COOKIE_HTTPONLY should be True')
        
        self.stdout.write('Django Settings: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def check_database_security(self):
        """Check database configuration and security"""
        issues = []
        
        # Check if using SQLite in production
        if not settings.DEBUG and 'sqlite3' in settings.DATABASES['default']['ENGINE']:
            issues.append('Using SQLite in production - consider PostgreSQL')
        
        # Check for default database passwords
        db_password = settings.DATABASES['default'].get('PASSWORD', '')
        if db_password in ['', 'password', 'admin', '123456']:
            issues.append('Weak or default database password')
        
        self.stdout.write('Database Security: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def check_file_permissions(self):
        """Check file and directory permissions"""
        issues = []
        
        # Check media directory permissions
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            try:
                # Check if directory is writable
                test_file = os.path.join(media_root, '.security_check')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except (OSError, PermissionError):
                issues.append('Media directory is not writable')
        
        # Check static files
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            # Static files should exist and be readable
            if not os.access(static_root, os.R_OK):
                issues.append('Static files directory is not readable')
        
        self.stdout.write('File Permissions: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def check_user_accounts(self):
        """Check user account security"""
        issues = []
        
        # Check for users with weak passwords (this is a simplified check)
        weak_password_users = User.objects.filter(
            password__in=['pbkdf2_sha256$1$', 'password', '']
        )
        if weak_password_users.exists():
            issues.append(f'{weak_password_users.count()} users with potentially weak passwords')
        
        # Check for unverified users
        unverified_users = User.objects.filter(
            email_verified=False,
            is_active=True
        )
        if unverified_users.count() > 10:  # Allow some unverified users
            issues.append(f'{unverified_users.count()} unverified active users')
        
        # Check for inactive counselors
        inactive_counselors = Counselor.objects.filter(is_active=False)
        if inactive_counselors.exists():
            self.stdout.write(f'Info: {inactive_counselors.count()} inactive counselors')
        
        self.stdout.write('User Accounts: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def check_logging(self):
        """Check logging configuration"""
        issues = []
        
        # Check if logs directory exists
        logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
        if not os.path.exists(logs_dir):
            issues.append('Logs directory does not exist')
        
        # Check logging configuration
        if not hasattr(settings, 'LOGGING'):
            issues.append('Logging configuration not found')
        
        # Check if security log file exists
        security_log = os.path.join(logs_dir, 'security.log')
        if not os.path.exists(security_log):
            # Try to create it
            try:
                with open(security_log, 'a'):
                    pass
            except (OSError, PermissionError):
                issues.append('Cannot create security log file')
        
        self.stdout.write('Logging: ', ending='')
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ OK'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Issues found'))
        
        return issues
    
    def fix_issues(self, issues, options):
        """Attempt to fix security issues automatically"""
        fixed_count = 0
        
        for issue in issues:
            if 'Logs directory does not exist' in issue:
                try:
                    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
                    os.makedirs(logs_dir, exist_ok=True)
                    self.stdout.write(f'  ✅ Created logs directory: {logs_dir}')
                    fixed_count += 1
                except OSError as e:
                    self.stdout.write(f'  ❌ Could not create logs directory: {e}')
            
            elif 'Cannot create security log file' in issue:
                try:
                    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
                    security_log = os.path.join(logs_dir, 'security.log')
                    with open(security_log, 'a'):
                        pass
                    self.stdout.write(f'  ✅ Created security log file')
                    fixed_count += 1
                except OSError as e:
                    self.stdout.write(f'  ❌ Could not create security log: {e}')
        
        self.stdout.write(f'\n✅ Fixed {fixed_count} issues automatically')
        
        # Show remaining issues that need manual attention
        remaining_issues = len(issues) - fixed_count
        if remaining_issues > 0:
            self.stdout.write(f'⚠️  {remaining_issues} issues require manual attention')
            self.show_manual_fixes()
    
    def show_manual_fixes(self):
        """Show instructions for manual fixes"""
        self.stdout.write('\nManual fixes required:')
        self.stdout.write('1. Set environment variables in .env file:')
        self.stdout.write('   - DJANGO_SECRET_KEY=your-secret-key')
        self.stdout.write('   - DJANGO_DEBUG=False (for production)')
        self.stdout.write('   - EMAIL_HOST_USER=your-email@domain.com')
        self.stdout.write('   - OPENAI_API_KEY=your-openai-key')
        self.stdout.write('\n2. For production deployment:')
        self.stdout.write('   - Migrate to PostgreSQL database')
        self.stdout.write('   - Set strong database passwords')
        self.stdout.write('   - Enable HTTPS/SSL')
        self.stdout.write('   - Review user accounts and permissions')
        self.stdout.write('\n3. Run: python manage.py check --deploy')
