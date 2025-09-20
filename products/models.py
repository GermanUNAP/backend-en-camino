from mongoengine import Document, StringField, DecimalField, IntField, BooleanField, DateTimeField, ReferenceField, ListField, URLField, FloatField
from stores.models import Store

class Product(Document):
    store = ReferenceField(Store, required=True, reverse_delete_rule=None)
    name = StringField(max_length=255, required=True)
    description = StringField(blank=True)
    price = DecimalField(precision=2, required=True)
    
    images = ListField(URLField(), default=list, blank=True)
    is_featured = BooleanField(default=False)
    tags = ListField(StringField(max_length=50), default=list, blank=True)
    
    category = StringField(max_length=100, blank=True)
    stock = IntField(default=0)
    sku = StringField(max_length=50, blank=True)
    brand = StringField(max_length=100, blank=True)
    materials = StringField(blank=True)
    discount_price = DecimalField(precision=2, blank=True, null=True)
    
    views = IntField(default=0)
    sells_count = IntField(default=0)
    comments_count = IntField(default=0)
    average_rating = FloatField(default=0)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    image_url = URLField(blank=True)

    meta = {
        'collection': 'products',
        'indexes': ['store', 'category', 'tags', 'created_at'],
        'ordering': ['-created_at']
    }

    def __str__(self):
        return self.name