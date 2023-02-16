# routing.py
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    # re_path(r"ws/post_list/", consumers.PostLikeConsumer.as_asgi()),
    re_path(r"ws/test/$", consumers.MyConsumer.as_asgi()),
]
