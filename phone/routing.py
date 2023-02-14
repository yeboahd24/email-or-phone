# routing.py
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    # re_path(r'ws/post/like/(?P<post_id>\w+)/$', consumers.PostLikeConsumer),
    re_path(r'ws/post/(?P<post_id>[0-9]+)/like/$', consumers.PostLikeConsumer.as_asgi()),

]
