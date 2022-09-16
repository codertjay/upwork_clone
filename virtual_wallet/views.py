# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import LoggedInPermission
from virtual_wallet.serializers import WalletSerializer


class WalletAPIView(APIView):
    """
    This returns the wallet balance of the logged-in user and all his require details
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        serializer = WalletSerializer(instance=self.request.user.wallet)
        return Response(serializer.data, status=200)

