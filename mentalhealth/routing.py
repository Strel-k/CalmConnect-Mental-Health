from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
re_path(r'ws/live-session/(?P<room_id>\w+)/$',
consumers.LiveSessionConsumer.as_asgi()),
re_path(r'ws/chat/(?P<room_id>\w+)/$',
consumers.ChatConsumer.as_asgi()),
re_path(r'ws/notifications/$',
consumers.NotificationConsumer.as_asgi()),
re_path(r'ws/test/$',
consumers.TestConsumer.as_asgi()),
]