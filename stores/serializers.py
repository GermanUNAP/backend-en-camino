from rest_framework import serializers
from .models import Store, City
from accounts.serializers import CustomUserSerializer

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "province_id", "department_id", "slug"]

class StoreSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']