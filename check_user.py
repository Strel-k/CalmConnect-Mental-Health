import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import CustomUser

user = CustomUser.objects.filter(email='fdave.pararuan@clsu2.edu.ph').first()
print('User exists:', user is not None)
if user:
    print('is_active:', user.is_active)
    print('email_verified:', user.email_verified)
