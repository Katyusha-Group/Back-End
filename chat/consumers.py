from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from chat.models import Message, Chat
from chat.scripts.chat_views import get_or_create_user_contact, get_current_chat


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        messages = Chat.objects.get_20_last_messages(data['chatId'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_messages(content)

    def new_message(self, data):
        user_contact = get_or_create_user_contact(data['from'])
        message = Message.objects.create(
            contact=user_contact,
            content=data['message'])
        current_chat = get_current_chat(data['chatId'])
        current_chat.messages.add(message)
        current_chat.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages: [Message]):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message: Message):
        return {
            'id': message.id,
            'author': message.author.user.username,
            'content': message.content,
            'timestamp': str(message.created_at)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_messages(self, content):
        self.send(text_data=json.dumps(content))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
