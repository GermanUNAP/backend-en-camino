from django.db import models
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("card", "Credit Card"),
        ("yape", "Yape"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment_detail")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="card")
    token_id = models.CharField(max_length=100, blank=True)
    charge_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    yape_image_url = models.URLField(blank=True, null=True)