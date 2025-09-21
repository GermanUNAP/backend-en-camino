from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    images: List[str] = []
    is_featured: bool = False
    tags: List[str] = []
    category: Optional[str] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    materials: Optional[str] = None
    discount_price: Optional[Decimal] = None

class ProductCreate(ProductBase):
    store_id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    # ... (todos opcionales)

class Product(ProductBase):
    id: str
    store_id: str
    views: int = 0
    sells_count: int = 0
    comments_count: int = 0
    average_rating: float = 0.0
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None

    class Config:
        from_attributes = True