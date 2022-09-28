from rest_framework import serializers
from django.contrib.auth import get_user_model
from chats.models import Message, Conversation
from users.serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
        )

    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data

    def get_to_user(self, obj):
        return UserSerializer(obj.to_user).data


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "name", "other_user", "last_message")

    def get_last_message(self, obj):
        """
        this get the last message sent from the conversation

        """
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        """
        this enables getting the other user of a message using the id of the user from the
        conversation name
        :param obj:
        :return:
        """
        user_ids = obj.name.split("__")
        context = {}
        for user_id in user_ids:
            if user_id != self.context["user"].id:
                # This is the other participant
                other_user = User.objects.get(id=user_id)
                return UserProfileSerializer(other_user.user_profile, context=context).data
