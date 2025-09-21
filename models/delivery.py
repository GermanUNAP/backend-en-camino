from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class VehicleTypeEnum(str, Enum):
    car = "car"
    motorcycle = "motorcycle"
    bike = "bike"

class AvailabilityStatusEnum(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"

class RangeTypeEnum(str, Enum):
    city = "city"
    city_to_city = "city_to_city"
    national = "national"

class DeliveryPointBase(BaseModel):
    name: str
    address: str
    city: str
    range_type: RangeTypeEnum
    contact_phone: Optional[str] = None
    working_hours: Optional[dict] = None

class DeliveryPointCreate(DeliveryPointBase):
    pass

class DeliveryPoint(DeliveryPointBase):
    id: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    orders_ids: List[str] = []
    assigned_orders_ids: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShipperBase(BaseModel):
    vehicle_type: VehicleTypeEnum
    license_plate: Optional[str] = None
    current_location: Optional[str] = None
    availability_status: AvailabilityStatusEnum = AvailabilityStatusEnum.available

class ShipperCreate(ShipperBase):
    pass

class Shipper(ShipperBase):
    id: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    orders_ids: List[str] = []
    assigned_orders_ids: List[str] = []
    total_deliveries: int = 0
    successful_deliveries: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeliveryTrackingEvent(BaseModel):
    order_id: str
    event_type: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None
    responsible_user_id: Optional[str] = None
    notes: Optional[str] = None
    estimated_time: Optional[datetime] = None