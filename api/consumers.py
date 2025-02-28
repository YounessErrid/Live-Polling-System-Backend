# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import Poll, Choice
# from asgiref.sync import sync_to_async

# class PollConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.poll_id = self.scope['url_route']['kwargs']['poll_id']
#         self.poll_group_name = f'poll_{self.poll_id}'

#         # Join room group
#         await self.channel_layer.group_add(self.poll_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.poll_group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         choice_id = data.get('choice_id')

#         if choice_id:
#             choice = await sync_to_async(Choice.objects.get)(id=choice_id)
#             choice.votes += 1
#             await sync_to_async(choice.save)()

#             # Send updated poll data to group
#             await self.channel_layer.group_send(
#                 self.poll_group_name,
#                 {
#                     'type': 'poll_update',
#                     'poll_id': self.poll_id
#                 }
#             )

#     async def poll_update(self, event):
#         poll_id = event['poll_id']
#         poll = await sync_to_async(Poll.objects.get)(id=poll_id)
#         choices = await sync_to_async(list)(poll.choices.all().values('id', 'choice_text', 'votes'))

#         await self.send(text_data=json.dumps({
#             'poll_id': poll_id,
#             'choices': choices
#         }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "poll_updates"

        # Add user to WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from WebSocket group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "new_poll":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_poll",
                    "poll": data["poll"],  # Send poll data to all clients
                },
            )

    async def broadcast_poll(self, event):
        # Send new poll data to frontend
        await self.send(text_data=json.dumps({"type": "new_poll", "poll": event["poll"]}))
