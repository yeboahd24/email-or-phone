# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Post

class PostLikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        post_id = self.scope['url_route']['kwargs']['post_id']
        self.post_id = post_id
        self.post_group_name = f'post_like_{post_id}'

        # Join the post's group
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the post's group
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_post(self, post_id):
        return Post.objects.get(id=post_id)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        post_id = text_data_json['post_id']
        action = text_data_json['action']
        print('action', action)

        if action == 'like':
            post = await self.get_post(post_id)
            post.like_count += 1
            post.save()
            await self.send_like_update(post.like_count)

    async def send_like_update(self, like_count):
        # Send the update to the post's group
        await self.channel_layer.group_send(
            self.post_group_name,
            {
                'type': 'post_like_update',
                'like_count': like_count
            }
        )

    async def post_like_update(self, event):
        # Send the update to the client
        await self.send(text_data=json.dumps({
            'like_count': event['like_count']
        }))


