import os
import sys
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings

class Command(BaseCommand):
    help = 'Run the development server with ASGI support for WebSockets'

    def handle(self, *args, **options):
        # Set the environment variable for Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

        # Import and run Daphne
        try:
            from daphne.cli import CommandLineInterface

            # Use Daphne's CLI to run the server
            cli = CommandLineInterface()
            cli.run([
                'daphne',
                '-b', '0.0.0.0',
                '-p', '8000',
                'calmconnect_backend.asgi:application'
            ])

        except ImportError:
            self.stdout.write(
                self.style.ERROR('Daphne not installed. Installing...')
            )
            os.system('pip install daphne')
            self.stdout.write(
                self.style.SUCCESS('Please restart the server.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting ASGI server: {e}')
            )