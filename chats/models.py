from django.db import models
from users.models import User


class Contact(models.Model):
    user = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.user.email


class Message(models.Model):
    contact = models.ForeignKey(Contact, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contact.user.email


class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name="chat")
    messages = models.ManyToManyField(Message, blank=True)

    def last_ten_messages(self):
        return self.messages.objects.order_by("-timestamp").all()[:10]

    def __str__(self):
        return f"{self.pk}"
