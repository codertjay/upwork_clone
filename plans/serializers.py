from rest_framework import serializers

from .models import Plan


class PlanSerializer(serializers.ModelSerializer):
    """This  plan is meant to list, create, delete,update  subscription plan(s)
    Note
    """

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "plan_type",
            "plan_status",
            "paypal_plan_id",
            "price",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", "paypal_plan_id"]
