import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Setup Django
django.setup()

from mentalhealth.models import CustomUser

def create_admin_user():
    username = 'hansa'
    password = 'hansa'
    email = 'admin@hansa.com'  # Default email

    # Check if user already exists
    if CustomUser.objects.filter(username=username).exists():
        print(f"Admin user '{username}' already exists.")
        return

    # Create superuser
    try:
        # Generate unique student_id
        base_student_id = 'admin001'
        student_id = base_student_id
        counter = 1
        while CustomUser.objects.filter(student_id=student_id).exists():
            counter += 1
            student_id = f'admin{counter:03d}'

        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name='Admin User',
            age=0,
            gender='Prefer not to say',
            college='CBA',
            program='Administration',
            year_level='4',
            student_id=student_id
        )
        print(f"Admin user '{username}' created successfully with student_id '{student_id}'.")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user()
