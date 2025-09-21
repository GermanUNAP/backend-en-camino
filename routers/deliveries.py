from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from models.delivery import DeliveryPointCreate, DeliveryPoint, ShipperCreate, Shipper, DeliveryTrackingEvent
from crud.delivery import create_delivery_point, get_delivery_point, create_shipper, get_shipper, update_shipper_location, create_tracking_event, get_shipper_dashboard
from utils.auth import get_current_active_user

router = APIRouter()

@router.post("/points/", response_model=DeliveryPoint)
async def create_delivery_point(point: DeliveryPointCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "delivery_point":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_delivery_point(point, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Delivery point creation failed")
    return result

@router.get("/points/{point_id}", response_model=DeliveryPoint)
async def read_delivery_point(point_id: str, current_user: dict = Depends(get_current_active_user)):
    point = await get_delivery_point(point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Delivery point not found")
    if current_user["role"] != "admin" and point["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return point

@router.post("/shippers/", response_model=Shipper)
async def create_shipper(shipper: ShipperCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "shipper":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_shipper(shipper, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Shipper creation failed")
    return result

@router.get("/shippers/{shipper_id}", response_model=Shipper)
async def read_shipper(shipper_id: str, current_user: dict = Depends(get_current_active_user)):
    shipper = await get_shipper(shipper_id)
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper not found")
    if current_user["role"] != "admin" and shipper["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return shipper

@router.put("/shippers/{shipper_id}/location")
async def update_location(shipper_id: str, latitude: float, longitude: float, current_location: str, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "shipper":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await update_shipper_location(shipper_id, latitude, longitude, current_location, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Location update failed")
    return result

@router.get("/shippers/dashboard", response_model=List[dict])
async def shipper_dashboard(current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "shipper":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await get_shipper_dashboard(current_user["id"])

@router.post("/tracking/events/", response_model=DeliveryTrackingEvent)
async def create_new_tracking_event(event: DeliveryTrackingEvent, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] not in ["delivery_point", "shipper"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_tracking_event(event, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Tracking event creation failed")
    return result