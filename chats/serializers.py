from rest_framework import serializers

from chats.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        models = Chat
        #  using all the fields for now
        fields = ["__all__"]
