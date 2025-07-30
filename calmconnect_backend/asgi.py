"""
ASGI config for calmconnect_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# Temporarily removed for testing:
# from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')


def get_websocket_urlpatterns():
    # Import here so Django is fully initialized
    from mentalhealth.routing import websocket_urlpatterns
    return websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
            URLRouter(
            get_websocket_urlpatterns()
        )
    ),
})
