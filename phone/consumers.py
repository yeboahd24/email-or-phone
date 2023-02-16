from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Post
import json
from django.template.loader import get_template


class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "test_group"
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        print("Connected to {}".format(self.group_name))
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        print("Disconnected from {}".format(self.group_name))

    def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "update_post_likes":
            post_id = data["post_id"]
            post = Post.objects.get(id=post_id)

            # update the post in the DOM
            template = get_template("template.html")
            html = template.render({"post": post, "all_posts": Post.objects.all()})
            self.send(text_data=json.dumps({"html": html}))

    def update_post_likes(self, event):
        post_id = event["post_id"]
        post = Post.objects.get(id=post_id)

        # broadcast the updated post to all connected clients
        template = get_template("template.html")
        html = template.render({"post": post, "all_posts": Post.objects.all()})
        self.send(text_data=json.dumps({"html": html}))

    def render_posts(self):
        all_posts = Post.objects.all()
        template = get_template("template.html")
        html = template.render({"all_posts": all_posts})
        return html

    def send_update(self, html):
        message = {"html": html}
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {"type": "send_html", "message": message}
        )

    def send_html(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))
