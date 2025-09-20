from rest_framework import serializers
from .models import SubscriptionPlan, Payment, PlanDefinition

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"

class PlanDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanDefinition
        fields = "__all__"