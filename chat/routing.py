from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
	re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()), #here to make it wss?? we need to change the http to https
]

