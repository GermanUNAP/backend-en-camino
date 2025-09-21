from database import db
from models.order import OrderCreate, OrderUpdate, TrackingEvent
from typing import List, Optional
from datetime import datetime

async def create_order(order: OrderCreate, buyer_id: str) -> Optional[dict]:
    order_dict = order.dict()
    order_dict["buyer_id"] = buyer_id
    order_dict["tracking_number"] = f"TRK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    order_dict["tracking_history"] = [{"event_type": "created", "timestamp": datetime.utcnow(), "notes": "Order created"}]
    # Calcular total_price si no está
    if "total_price" not in order_dict or not order_dict["total_price"]:
        order_dict["total_price"] = sum(item.price * item.quantity for item in order.items)
    return db.insert_one("orders", order_dict)

async def get_order(order_id: str) -> Optional[dict]:
    return db.find_one("orders", {"_id": order_id})

async def get_orders_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[dict]:
    return db.find("orders", {"buyer_id": user_id}, limit=limit)

async def update_order(order_id: str, order_update: OrderUpdate, buyer_id: str) -> Optional[dict]:
    query = {"_id": order_id, "buyer_id": buyer_id}
    update_dict = order_update.dict(exclude_unset=True)
    if "tracking_history" in update_dict:
        update_dict["tracking_history"] = order_update.tracking_history + [TrackingEvent(**event).dict() for event in update_dict["tracking_history"]]
    update_dict["updated_at"] = datetime.utcnow()
    if db.update_one("orders", query, update_dict):
        return await get_order(order_id)
    return None

async def add_tracking_event(order_id: str, event: TrackingEvent, user_id: str) -> bool:
    query = {"_id": order_id, "buyer_id": user_id}
    event_dict = event.dict()
    event_dict["timestamp"] = datetime.utcnow()
    event_dict["responsible_user_id"] = user_id
    db.update_one("orders", query, {"$push": {"tracking_history": event_dict}})
    # Update status based on event_type
    status_map = {"delivered": "delivered", "cancelled": "cancelled"}
    if event.event_type in status_map:
        db.update_one("orders", query, {"status": status_map[event.event_type]})
    return True

async def delete_order(order_id: str, buyer_id: str) -> bool:
    query = {"_id": order_id, "buyer_id": buyer_id}
    return db.delete_one("orders", query)