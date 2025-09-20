from mongoengine import Document, StringField, DecimalField, IntField, DateTimeField, ReferenceField, BooleanField, ListField, DictField, FloatField
from accounts.models import CustomUser
from stores.models import Store
from payments.models import Payment

class OrderStatus(Document):
    name = StringField(max_length=20, required=True)
    description = StringField(blank=True)
    
    meta = {
        'collection': 'order_statuses'
    }

class OrderItem(Document):
    order = ReferenceField('Order', required=True, reverse_delete_rule=None)
    product = ReferenceField('Product', required=True, reverse_delete_rule=None)
    quantity = IntField(default=1, required=True)
    price = DecimalField(precision=2, required=True)
    
    meta = {
        'collection': 'order_items',
        'indexes': ['order', 'product']
    }

class Order(Document):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    buyer = ReferenceField(CustomUser, required=True, reverse_delete_rule=None)
    store = ReferenceField(Store, required=True, reverse_delete_rule=None)
    total_price = DecimalField(precision=2, required=True)
    status = StringField(max_length=20, choices=[choice[0] for choice in STATUS_CHOICES], default="pending")
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    delivery_address = StringField(max_length=255, required=True)
    tracking_number = StringField(max_length=100, blank=True)
    
    payment = ReferenceField(Payment, reverse_delete_rule=None, null=True, blank=True)
    
    # Tracking Information
    delivery_latitude = FloatField(blank=True, null=True)
    delivery_longitude = FloatField(blank=True, null=True)
    delivery_notes = StringField(blank=True)
    estimated_delivery_time = DateTimeField(blank=True, null=True)
    actual_delivery_time = DateTimeField(blank=True, null=True)
    
    # Delivery Point Assignment
    assigned_delivery_point_id = StringField(max_length=100, blank=True)
    assigned_shipper_id = StringField(max_length=100, blank=True)
    
    # Tracking History
    tracking_history = ListField(DictField(), default=list, blank=True)
    
    items = ListField(ReferenceField(OrderItem, reverse_delete_rule=None), default=list, blank=True)

    meta = {
        'collection': 'orders',
        'indexes': ['buyer', 'store', 'status', 'created_at', 'tracking_number'],
        'ordering': ['-created_at']
    }

    def __str__(self):
        return f"Order {self.id} - {self.buyer.username}"