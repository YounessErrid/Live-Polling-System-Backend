# from django.urls import re_path
# from api.consumers import PollConsumer  # Import your consumer

# websocket_urlpatterns = [
#     re_path(r'ws/poll/(?P<poll_id>\d+)/$', PollConsumer.as_asgi()),
# ]

from django.urls import re_path
from .consumers import PollConsumer  # Make sure the consumer is correctly imported

websocket_urlpatterns = [
    re_path(r'ws/polls/$', PollConsumer.as_asgi()),  # WebSocket endpoint for polls
]