from rest_framework import serializers
from .models import DeliveryPoint, Shipper, DeliveryTracking
from accounts.serializers import CustomUserSerializer
from orders.serializers import OrderSerializer

class DeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = "__all__"
        read_only_fields = ['timestamp']

class DeliveryPointSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = DeliveryPoint
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']

class ShipperSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Shipper
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']