from database import db
from models.delivery import DeliveryPointCreate, ShipperCreate, DeliveryTrackingEvent
from typing import List, Optional
from datetime import datetime

async def create_delivery_point(point: DeliveryPointCreate, user_id: str) -> Optional[dict]:
    point_dict = point.dict()
    point_dict["user_id"] = user_id
    point_dict["orders_ids"] = []
    point_dict["assigned_orders_ids"] = []
    point_dict["created_at"] = datetime.utcnow()
    point_dict["updated_at"] = datetime.utcnow()
    return db.insert_one("delivery_points", point_dict)

async def get_delivery_point(point_id: str) -> Optional[dict]:
    return db.find_one("delivery_points", {"_id": point_id})

async def create_shipper(shipper: ShipperCreate, user_id: str) -> Optional[dict]:
    shipper_dict = shipper.dict()
    shipper_dict["user_id"] = user_id
    shipper_dict["orders_ids"] = []
    shipper_dict["assigned_orders_ids"] = []
    shipper_dict["created_at"] = datetime.utcnow()
    shipper_dict["updated_at"] = datetime.utcnow()
    return db.insert_one("shippers", shipper_dict)

async def get_shipper(shipper_id: str) -> Optional[dict]:
    return db.find_one("shippers", {"_id": shipper_id})

async def update_shipper_location(shipper_id: str, latitude: float, longitude: float, current_location: str, user_id: str) -> bool:
    query = {"_id": shipper_id, "user_id": user_id}
    update = {"latitude": latitude, "longitude": longitude, "current_location": current_location, "updated_at": datetime.utcnow()}
    return db.update_one("shippers", query, update)

async def get_shipper_dashboard(shipper_id: str) -> List[dict]:
    shipper = await get_shipper(shipper_id)
    if not shipper:
        return []
    order_ids = shipper.get("assigned_orders_ids", [])
    return db.find("orders", {"_id": {"$in": order_ids}})

async def create_tracking_event(event: DeliveryTrackingEvent, user_id: str) -> Optional[dict]:
    event_dict = event.dict()
    event_dict["user_id"] = user_id
    event_dict["created_at"] = datetime.utcnow()
    return db.insert_one("delivery_tracking", event_dict)