import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import CustomUser

user = CustomUser.objects.filter(username='hansa').first()
if user:
    print(f"User 'hansa' exists.")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Is staff: {user.is_staff}")
    print(f"Email: {user.email}")
else:
    print("User 'hansa' does not exist.")
