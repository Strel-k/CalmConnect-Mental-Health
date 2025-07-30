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
            from daphne.server import Server
            from daphne.endpoints import build_endpoint_description_strings
            from calmconnect_backend.asgi import application
            
            # Build endpoint description
            endpoints = build_endpoint_description_strings(
                host='0.0.0.0',
                port=8000,
                application=application
            )
            
            # Create and run server
            server = Server(
                application=application,
                endpoints=endpoints,
                signal_handlers=True,
                action_logger=None,
                http_timeout=120,
                request_buffer_size=8192,
                max_buffer_size=32768,
                websocket_timeout=120,
                websocket_connect_timeout=20,
                verbosity=1,
            )
            
            self.stdout.write(
                self.style.SUCCESS('Starting ASGI server with WebSocket support...')
            )
            self.stdout.write(
                self.style.SUCCESS('Server running at http://0.0.0.0:8000/')
            )
            self.stdout.write(
                self.style.SUCCESS('WebSocket support enabled!')
            )
            
            server.run()
            
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