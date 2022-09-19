import uuid

from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import LoggedInPermission
from transactions.models import Transaction
from virtual_wallets.serializers import WalletSerializer, CreatePaymentSerializer, ApprovePaymentSerializer, \
    WithdrawFundSerializer
from virtual_wallets.utils import create_paypal_payment, verify_paypal_payment, create_paypal_payout


class WalletAPIView(APIView):
    """
    This returns the wallet balance of the logged-in user and all his requirement details
    """
    permission_classes = [LoggedInPermission]

    def get(self, request, *args, **kwargs):
        serializer = WalletSerializer(instance=self.request.user.wallet)
        return Response(serializer.data, status=200)


class CreatePaymentAPIView(APIView):
    """
    this class enables creating a payment for the user which is used to complete the payment on the frontend.

    There are two steps in PayPal
    1: create order
    2:approve order

    So right now I am not allowing the frontend developer the use the javascript produced by PayPal to process the request
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get("amount")
        #  create the payment on PAYPAL
        response = create_paypal_payment(amount)
        if not response:
            return Response({"error": "An error occurred creating your payment"}, status=400)
        # create a transaction
        transaction = Transaction.objects.create(
            user=request.user,
            transaction_id=response.get("id"),
            transaction_type="CREDIT",
            transaction_stage="PROCESSING",
            transaction_category="AMOUNT FUNDING",
            current_balance=request.user.wallet.balance,
            previous_balance=request.user.wallet.balance,
            amount=amount,
        )
        #  the response is a json because the create_paypal_payment returns response.json() so we dont need to call
        #  response.json all over again
        return Response(response, status=200)


class ApprovePaymentAPIView(APIView):
    """
    this funds the user wallet using the amount ,and it also sends the PayPal
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = ApprovePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_id = serializer.validated_data.get("transaction_id")
        if not verify_paypal_payment(transaction_id):
            return Response({"error": "Payment was not approved"}, status=400)
        transaction = Transaction.objects.filter(transaction_stage="PROCESSING", transaction_id=transaction_id).first()
        if not transaction:
            return Response({"error": "Transaction id has been used before or it doesn't exist"}, status=400)
        user_wallet = request.user.wallet
        #  add the amount the user paid using the transaction we created which has the amount the user create to pay for
        user_wallet.balance += transaction.amount
        user_wallet.save()
        #  update the current balance of the user
        transaction.current_balance = user_wallet.balance
        transaction.save()
        return Response({"message": "Successfully fund wallet"}, status=200)


class WithdrawFundAPIView(APIView):
    """
    this class is meant to withdraw fund of a user from his balance
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = WithdrawFundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp")
        amount = serializer.validated_data.get("amount")
        if not request.user.validate_email_otp(otp):
            return Response({"error": "OTP not valid"}, status=400)
        user_wallet = request.user.wallet
        if not user_wallet.can_withdraw(amount):
            return Response({"error": "Insufficient fund"}, status=400)
        # create a transaction with an instance . which enable use to dynamically add fields base on the response
        transaction = Transaction()
        transaction.transaction_id = uuid.uuid4().hex
        transaction.user = request.user
        transaction.current_balance = user_wallet.balance
        transaction.previous_balance = user_wallet.balance
        transaction.transaction_type = "DEBIT"
        transaction.amount = amount
        transaction.transaction_category = "WITHDRAWAL"
        # making payment to the logged-in user email address . and if he does not
        # wish to use that email then he has to change his email address
        response = create_paypal_payout(amount=amount, email=request.user.email,
                                        transaction_id=transaction.transaction_id)
        if not response:
            transaction.transaction_stage = "FAILED"
            transaction.save()
            return Response({"error": "An error occurred .we are currently working on it"}, status=400)
        if response.get("batch_status") == "PENDING":
            transaction.transaction_stage = "PROCESSING"
            transaction.save()
        return Response(response, status=200)
