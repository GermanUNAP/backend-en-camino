from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    quantity: int = 1
    price: Decimal

class TrackingEvent(BaseModel):
    event_type: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None
    notes: Optional[str] = None

class OrderBase(BaseModel):
    store_id: str
    items: List[OrderItem]
    delivery_address: str
    total_price: Decimal
    status: OrderStatusEnum = OrderStatusEnum.pending

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    # ... (otros opcionales)

class Order(OrderBase):
    id: str
    buyer_id: str
    tracking_number: Optional[str] = None
    payment_id: Optional[str] = None
    delivery_notes: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    assigned_delivery_point_id: Optional[str] = None
    assigned_shipper_id: Optional[str] = None
    tracking_history: List[TrackingEvent] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True