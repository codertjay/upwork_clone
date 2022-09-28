import json
from uuid import UUID

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer
from chats.serializers import MessageSerializer

from chats.models import Conversation, Message

User = get_user_model()


# Note: You might notice we are always converting the user.id to string
# and that is because the user.id is a UUID and  UUID cant be serialized
# So we need to convert it to string and also the conversation__name will be converted
# to string since it was created by adding two uuid which makes it a uuid also

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


def get_or_create_conversation(user, name):
    """
    :param user: The logged-in user
    :param name: user1_id__user2__id
    :return: conversation
    """
    #  filter base on the conversation
    conversation = Conversation.objects.filter(name=name)
    if conversation.exists():
        #  this returns the conversation
        return conversation.first()
    user_ids = name.split("__")
    #  Get all the user conversations in which the logged-in user is in the conversation
    user_conversation_qs = Conversation.objects.filter(name__icontains=str(user.id))
    #  if the user conversation exists
    if user_conversation_qs.exists():
        for user_id in user_ids:
            # use the order user id
            if user_id != str(user.id):
                conversation_qs = user_conversation_qs.filter(name__icontains=user_id)
                if conversation_qs.exists():
                    return conversation_qs.first()
    else:
        # if the conversation does not exist from the above then we create a new one
        conversation, created = Conversation.objects.get_or_create(name=name)
        return conversation


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        self.conversation_name = (
            f"{self.scope['url_route']['kwargs']['conversation_name']}"
        )
        # validate the conversation name
        user_ids = self.conversation_name.split("__")
        #  in here I split the conversation name which is user1_id__user2__id
        # then I check if the ids exists
        for user_id in user_ids:
            user = User.objects.filter(id=user_id)
            if not user.exists():
                self.disconnect(code=1014)

        # the get the conversation with the user id passed in the url which is user_id__other_user_id
        self.conversation = get_or_create_conversation(self.user, str(self.conversation_name))
        # update the conversation name if the user_id is user2__id__user1__id
        self.conversation_name = str(self.conversation.name)

        # set the channel name
        async_to_sync(self.channel_layer.group_add)(
            str(self.conversation_name),
            self.channel_name,
        )
        # show list of online users
        self.send_json(
            {
                "type": "online_user_list",
                "users": [str(user.id) for user in self.conversation.online.all()],
            }
        )

        # send and event to every one on this conversation that this logged-in user just join
        async_to_sync(self.channel_layer.group_send)(
            str(self.conversation_name),
            {
                "type": "user_join",
                "user_id": str(self.user.id),
            },
        )

        # add the current user online users
        self.conversation.online.add(self.user)

        #  this shows the last ten message on the conversation
        messages = self.conversation.messages.all().order_by("-timestamp")[0:10]
        message_count = self.conversation.messages.all().count()
        self.send_json(
            {
                "type": "last_50_messages",
                "messages": MessageSerializer(messages, many=True).data,
                "has_more": message_count > 5,
            }
        )

    def disconnect(self, code):
        # Check if the users is authenticated and if he is  then I remove the user
        # from online users in the Conversation
        if self.user.is_authenticated:
            # send the leave event to the room
            self.conversation.online.remove(self.user)
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "user_leave",
                    "user_id": str(self.user.id),
                },
            )
        return super().disconnect(code)

    def get_receiver(self):
        #  it uses the id's in the conversation_name to get the receiver id
        user_ids = self.conversation_name.split("__")
        for user_id in user_ids:
            if user_id != str(self.user.id):
                # This is the receiver
                return User.objects.get(id=user_id)

    def receive_json(self, content, **kwargs):
        #  this receives json is used to receive any echo from the front end
        message_type = content["type"]

        if message_type == "read_messages":
            # the is used to read all messages by the receiver
            messages_to_me = self.conversation.messages.filter(to_user=self.user)
            messages_to_me.update(read=True)

            # Update the unread message count
            unread_count = Message.objects.filter(to_user=self.user, read=False).count()
            async_to_sync(self.channel_layer.group_send)(
                str(self.user.id) + "__notifications",
                {
                    "type": "unread_count",
                    "unread_count": unread_count,
                },
            )

        if message_type == "typing":
            #  this is to let the other user knows you are typing
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "typing",
                    "user_id": str(self.user.id),
                    "typing": content["typing"],
                },
            )

        if message_type == "chat_message":
            #  this is used to create message
            message = Message.objects.create(
                from_user=self.user,
                to_user=self.get_receiver(),
                content=content["message"],
                conversation=self.conversation,
            )

            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "chat_message_echo",
                    "user_id": str(self.user.id),
                    "message": MessageSerializer(message).data,
                },
            )

            # This is a path where the logged-in user could see all his or her
            # notifications from message received
            notification_group_name = str(self.get_receiver().id) + "__notifications"
            async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "user_id": str(self.user.id),
                    "message": MessageSerializer(message).data,
                },
            )
        if message_type == "is_online":
            # this returns boolean base on the other user online status
            # this check if the logged-in user count is greater than one the .it shows the other user is not online
            # because right now if it is only one that means the online user is 1
            async_to_sync(self.channel_layer.group_send)(
                str(self.conversation_name),
                {
                    "type": "is_online",
                    "is_online": self.conversation.online.count() > 1,
                },
            )

        return super().receive_json(content, **kwargs)

    def chat_message_echo(self, event):
        self.send_json(event)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)

    def typing(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)

    def is_online(self, event):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content):
        #  this  class method is created if you want to encode a json
        return json.dumps(content, cls=UUIDEncoder)


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.notification_group_name = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()

        # private notification group
        self.notification_group_name = str(self.user.id) + "__notifications"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

        # Send count of unread messages
        unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_count,
            }
        )

    def disconnect(self, code):
        print("code ", code)
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)
