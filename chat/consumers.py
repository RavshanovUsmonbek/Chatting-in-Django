# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message
from django.contrib.auth import get_user_model
from chat.models import Group, Contact

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        channel_name = int(data['channel_name'])
        user_id = int(data['user_id'])
        messages = Message.last_10_messages(channel_name,user_id)
        content = {
            'command': "messages",
            'messages': self.messages_to_json(messages)
        }
        self.send(text_data=json.dumps(content))


    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result


    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'created': str(message.created),
        }


    def new_message(self, data):
        author = data['from']
        channel_name = data['channel_name']
        author_user = User.objects.filter(username=author)[0]
        group = Group.objects.get(pk=int(channel_name))

        if group.is_real_group:
            message = Message.objects.create(
                author=author_user,
                to_group=group,
                is_broadcast=True,
                content = data['message'])
            message.save()
        else:
            user_id = int(data['user_id'])
            contact = group.contacts.get(owner_id=user_id)
            to_user = User.objects.get(pk=contact.user_id.id)
            message = Message.objects.create(
                author=author_user,
                to_user=to_user,
                is_broadcast=False,
                content = data['message'])
            message.save()

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.chat_send_message(content)

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
        # message = text_data_json['message']

        # Send message to room group

    def chat_send_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
        print('chat_message')
