from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from chats.models import Chat, Contact
from chats.serializers import ChatSerializer
from users.permissions import LoggedInPermission

User = get_user_model()


class ChatListCreateAPIView(ListCreateAPIView):
    permission_classes = [LoggedInPermission]
    serializer_class = ChatSerializer

    def get_user_contact(self, user_id):
        """this returns all the contacts made by the user"""
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise Http404
        contact = Contact.objects.filter(user=user).first()
        if not contact:
            raise Http404
        return contact

    def get_queryset(self):
        """this returns all the chat """
        user_id = self.request.query_params.get("user_id", None)
        if not user_id:
            raise Http404
        contact = self.get_user_contact(user_id)
        return contact.chat.all()


class ChatRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [LoggedInPermission]
    lookup_field = "pk"
