from rest_framework import serializers
from .models import Product
from stores.serializers import StoreSerializer

class ProductSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'views', 'sells_count', 'comments_count', 'average_rating']