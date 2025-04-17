from collections import defaultdict
import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    user_connections = defaultdict(int)

    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return

        self.room_group_name = 'chat_global11'
        user = self.scope['user']

        if self.user_connections[user.username] >= 5:
            await self.close(code=4001)
            return

        # Increment connection count
        self.user_connections[user.username] += 1

        # Add to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            user = self.scope['user']
            self.user_connections[user.username] -= 1
            if self.user_connections[user.username] <= 0:
                del self.user_connections[user.username]

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        if not self.is_valid_message(message):
            await self.send(text_data=json.dumps({
                'error': 'Invalid message'
            }))
            return
        user = self.scope['user']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    def is_valid_message(self, message):
        if not message or len(message) > 500:
            return False
        if re.search(r'<script', message, re.IGNORECASE):
            return False
        return True

    # @sync_to_async
    # def get_user_connections(self, user):
    #     return len(self.channel_layer.group_channels('chat_global'))
