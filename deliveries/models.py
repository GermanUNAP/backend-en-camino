from django.db import models
from accounts.models import CustomUser
from orders.models import Order

class DeliveryPoint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="delivery_points")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    range_type = models.CharField(
        max_length=100, 
        choices=(("city", "City Only"), ("city_to_city", "City to City"), ("national", "National"))
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    working_hours = models.JSONField(default=dict, blank=True)
    
    # IDs de órdenes en lugar de ManyToMany para evitar problemas
    orders_ids = models.JSONField(default=list, blank=True)
    assigned_orders_ids = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Shipper(models.Model):
    VEHICLE_CHOICES = (
        ("car", "Car"),
        ("motorcycle", "Motorcycle"),
        ("bike", "Bike"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="shippers")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    license_plate = models.CharField(max_length=50, blank=True)
    current_location = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    availability_status = models.CharField(
        max_length=20, 
        choices=(("available", "Available"), ("busy", "Busy"), ("offline", "Offline")), 
        default="available"
    )
    
    # IDs de órdenes en lugar de ManyToMany
    orders_ids = models.JSONField(default=list, blank=True)
    assigned_orders_ids = models.JSONField(default=list, blank=True)
    
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type}"

class DeliveryTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tracking_events")
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=50, 
        choices=(
            ("created", "Order Created"),
            ("payment_confirmed", "Payment Confirmed"),
            ("assigned_to_delivery_point", "Assigned to Delivery Point"),
            ("picked_up", "Picked Up from Store"),
            ("assigned_to_shipper", "Assigned to Shipper"),
            ("in_transit", "In Transit"),
            ("arrived_at_delivery_point", "Arrived at Delivery Point"),
            ("out_for_delivery", "Out for Delivery"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        )
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_description = models.CharField(max_length=255, blank=True)
    responsible_user_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    estimated_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.event_type} - {self.order.id}"