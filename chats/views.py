from django.http import Http404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from .models import Conversation, Message
from .paginators import MessagePagination

from .serializers import MessageSerializer, ConversationSerializer
from users.permissions import LoggedInPermission


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    this list the conversations of the logged-in user
    """
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        #  filter the conversation base on conversation name that contains the user id
        queryset = Conversation.objects.filter(
            name__contains=self.request.user.id
        )
        return queryset

    def get_serializer_context(self):
        """this enables adding the context to a serializer"""
        return {"request": self.request, "user": self.request.user}


class MessageViewSet(ListModelMixin, GenericViewSet):
    """"
    Returns
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        # check if the current user has access but if the user is a staff he has access to viewing the messages
        # notice I had to convert the user id to string that's because the id is currently a uuid
        if not str(self.request.user.id) in conversation_name.split("__") or self.request.user.is_staff is False:
            #  it raises an error if the user is not in this conversation
            raise Http404
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.id,
            )
            .filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset
