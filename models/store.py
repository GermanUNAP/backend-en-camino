from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class DeliveryRangeEnum(str, Enum):
    city = "city"
    city_to_city = "city_to_city"
    national = "national"

class SocialMediaLink(BaseModel):
    platform: str
    link: str

class StoreBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    cover_image: Optional[str] = None
    tags: List[str] = []
    store_images: List[str] = []
    social_media: List[SocialMediaLink] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    delivery_range: DeliveryRangeEnum = DeliveryRangeEnum.city

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    # ... (todos los campos opcionales)

class Store(StoreBase):
    id: str
    owner_id: str
    stars: float = 0.0
    views: int = 0
    clicks: int = 0
    whatsapp_clicks: int = 0
    product_sells: int = 0
    followers: int = 0
    opinions_count: int = 0
    web_clicks: int = 0
    current_plan: Optional[dict] = None
    payment_history: List[dict] = []
    is_online_store: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True