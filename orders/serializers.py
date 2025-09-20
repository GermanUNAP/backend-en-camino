from rest_framework import serializers
from .models import Order, OrderItem
from accounts.serializers import CustomUserSerializer
from stores.serializers import StoreSerializer
from products.serializers import ProductSerializer
from payments.serializers import PaymentSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    buyer = CustomUserSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "buyer", "store", "total_price", "status", "created_at", 
            "updated_at", "delivery_address", "tracking_number", "items", 
            "payment", "delivery_latitude", "delivery_longitude", 
            "delivery_notes", "estimated_delivery_time", "actual_delivery_time",
            "assigned_delivery_point_id", "assigned_shipper_id", "tracking_history"
        ]
        read_only_fields = ['created_at', 'updated_at', 'tracking_history']