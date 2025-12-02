from django.core.management.base import BaseCommand
from mentalhealth.models import CustomUser

class Command(BaseCommand):
    help = 'Create a superuser for the application'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@calmconnect.edu.ph'
        password = options.get('password') or 'admin123!'

        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists.')
            )
            return

        # Generate unique student_id
        base_student_id = 'admin001'
        student_id = base_student_id
        counter = 1
        while CustomUser.objects.filter(student_id=student_id).exists():
            counter += 1
            student_id = f'admin{counter:03d}'

        try:
            user = CustomUser.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                full_name='Administrator',
                age=0,
                gender='Prefer not to say',
                college='CBA',
                program='Administration',
                year_level='4',
                student_id=student_id
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" created successfully!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Student ID: {student_id}\n'
                    f'Password: {password}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )