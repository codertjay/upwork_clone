from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from .models import Conversation, Message
from .paginators import MessagePagination

from .serializers import MessageSerializer, ConversationSerializer


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    this list the conversations of the logged-in user
    """
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"

    def get_queryset(self):
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

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.username,
            )
            .filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset
