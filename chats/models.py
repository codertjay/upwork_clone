import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Conversation(models.Model):
    """
    this is more of like a room where users contact each other .
    we use the user1_id__user2__id to create the name of the conversation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=User, blank=True)

    def get_online_count(self):
        # shows the number of online users in this conversation
        return self.online.count()

    def join(self, user):
        # add a user to the online user
        self.online.add(user)
        self.save()

    def leave(self, user):
        #  remove the user once he is not connected
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    """
    the message which is gotten by accessing the converation set
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_from_me"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_to_me"
    )
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.from_user.id} to {self.to_user.id}: {self.content} [{self.timestamp}]"
