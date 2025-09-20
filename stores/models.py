from mongoengine import Document, StringField, FloatField, IntField, BooleanField, DateTimeField, ReferenceField, ListField, DictField, URLField
from accounts.models import CustomUser

class City(Document):
    name = StringField(max_length=100, required=True)
    province_id = StringField(max_length=50, required=True)
    department_id = StringField(max_length=50, required=True)
    slug = StringField(max_length=100, unique=True, required=True)
    
    meta = {
        'collection': 'cities',
        'indexes': ['slug']
    }

class SocialMediaLink(Document):
    platform = StringField(max_length=50, required=True)
    link = StringField(max_length=500, required=True)
    
    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

class Store(Document):
    owner = ReferenceField(CustomUser, required=True, reverse_delete_rule=None)
    name = StringField(max_length=255, required=True)
    category = StringField(max_length=100, required=True)
    description = StringField(blank=True)
    city = StringField(max_length=100, blank=True)
    address = StringField(max_length=255, blank=True)
    phone = StringField(max_length=20, blank=True)
    cover_image = URLField(blank=True)
    
    tags = ListField(StringField(max_length=50), default=list, blank=True)
    store_images = ListField(URLField(), default=list, blank=True)
    social_media = ListField(DictField(), default=list, blank=True)
    
    latitude = FloatField(blank=True, null=True)
    longitude = FloatField(blank=True, null=True)
    stars = FloatField(default=0)
    views = IntField(default=0)
    clicks = IntField(default=0)
    whatsapp_clicks = IntField(default=0)
    product_sells = IntField(default=0)
    followers = IntField(default=0)
    opinions_count = IntField(default=0)
    web_clicks = IntField(default=0)
    
    current_plan = DictField(blank=True, null=True)
    payment_history = ListField(DictField(), default=list, blank=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_online_store = BooleanField(default=False)
    delivery_range = StringField(
        max_length=100, 
        choices=(("city", "City Only"), ("city_to_city", "City to City"), ("national", "National")), 
        default="city"
    )

    meta = {
        'collection': 'stores',
        'indexes': ['owner', 'category', 'city', 'created_at'],
        'ordering': ['-created_at']
    }

    def __str__(self):
        return self.name