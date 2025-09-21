from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.order import Order, OrderCreate, OrderUpdate, TrackingEvent
from crud.order import create_order, get_order, get_orders_by_user, update_order, add_tracking_event, delete_order
from utils.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Order)
async def create_new_order(order: OrderCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] not in ["buyer", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_order(order, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Order creation failed")
    return result

@router.get("/", response_model=List[Order])
async def read_orders(skip: int = 0, limit: int = 20, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] == "admin":
        orders = db.find("orders", {}, limit=limit)
    else:
        orders = await get_orders_by_user(current_user["id"], skip, limit)
    return orders

@router.get("/{order_id}", response_model=Order)
async def read_order(order_id: str, current_user: dict = Depends(get_current_active_user)):
    order = await get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] != "admin" and order["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order

@router.put("/{order_id}", response_model=Order)
async def update_existing_order(
    order_id: str, order: OrderUpdate, current_user: dict = Depends(get_current_active_user)
):
    order_db = await get_order(order_id)
    if not order_db:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] != "admin" and order_db["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await update_order(order_id, order, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Order update failed")
    return result

@router.post("/{order_id}/tracking")
async def add_order_tracking(
    order_id: str, event: TrackingEvent, current_user: dict = Depends(get_current_active_user)
):
    order = await get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] not in ["admin", "delivery_point", "shipper"] or (order["assigned_delivery_point_id"] != current_user.get("id") and order["assigned_shipper_id"] != current_user.get("id")):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await add_tracking_event(order_id, event, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Tracking event failed")
    return {"message": "Tracking event added"}

@router.delete("/{order_id}")
async def delete_order_endpoint(
    order_id: str, current_user: dict = Depends(get_current_active_user)
):
    order = await get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user["role"] != "admin" and order["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await delete_order(order_id, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Order deletion failed")
    return {"message": "Order deleted successfully"}