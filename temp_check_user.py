from django.conf import settings
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()
from mentalhealth.models import CustomUser
try:
    user = CustomUser.objects.get(email='fdave.pararuan@clsu2.edu.ph')
    print('User exists:', user.username)
    print('Active:', user.is_active)
    print('Verified:', user.email_verified)
except CustomUser.DoesNotExist:
    print('User does not exist')
except Exception as e:
    print('Error:', str(e))
