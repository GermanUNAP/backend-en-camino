from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from models.store import StoreCreate, Store, StoreUpdate, SocialMediaLink
from crud.store import create_store, get_store, get_stores, update_store, delete_store
from utils.auth import get_current_active_user
from database import db
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Store)
async def create_new_store(
    store: StoreCreate, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Crear nueva tienda virtual
    """
    if current_user["role"] not in ["store_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Solo store owners y admins pueden crear tiendas")
    
    # Convertir social_media de Pydantic a dict para MongoDB
    store_dict = store.dict()
    store_dict["owner_id"] = current_user["id"]
    store_dict["stars"] = 0.0
    store_dict["views"] = 0
    store_dict["clicks"] = 0
    store_dict["whatsapp_clicks"] = 0
    store_dict["product_sells"] = 0
    store_dict["followers"] = 0
    store_dict["opinions_count"] = 0
    store_dict["web_clicks"] = 0
    store_dict["current_plan"] = None
    store_dict["payment_history"] = []
    store_dict["is_online_store"] = False
    store_dict["created_at"] = datetime.utcnow()
    store_dict["updated_at"] = datetime.utcnow()
    
    result = await create_store(store_dict)
    if not result:
        raise HTTPException(status_code=400, detail="Error al crear la tienda")
    
    return result

@router.get("/", response_model=List[Store])
async def read_stores(
    skip: int = 0, 
    limit: int = 20, 
    category: Optional[str] = None, 
    city: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Listar tiendas con filtros
    """
    query = {}
    if category:
        query["category"] = category
    if city:
        query["city"] = city
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    stores = await get_stores(skip, limit, category, city)
    return stores

@router.get("/{store_id}", response_model=Store)
async def read_store_detail(store_id: str):
    """
    Obtener detalles completos de una tienda
    """
    store = await get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
    # Incrementar contador de vistas
    db.update_one("stores", {"_id": store_id}, {"$inc": {"views": 1}})
    
    # Enriquecer con productos
    products = db.find("products", {"store_id": store_id}, limit=12)
    store["products"] = products[:6]  # Primeros 6 productos
    store["total_products"] = len(products)
    
    return store

@router.put("/{store_id}", response_model=Store)
async def update_existing_store(
    store_id: str, 
    store_update: StoreUpdate, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualizar información de la tienda
    """
    existing_store = await get_store(store_id)
    if not existing_store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
    if current_user["role"] != "admin" and existing_store["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta tienda")
    
    update_dict = store_update.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await update_store(store_id, update_dict, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Error al actualizar la tienda")
    
    return result

@router.delete("/{store_id}")
async def delete_store_endpoint(
    store_id: str, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Eliminar tienda (solo dueño o admin)
    """
    existing_store = await get_store(store_id)
    if not existing_store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
    if current_user["role"] != "admin" and existing_store["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta tienda")
    
    # Eliminar productos relacionados
    db.delete_many("products", {"store_id": store_id})
    
    result = await delete_store(store_id, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Error al eliminar la tienda")
    
    return {"message": "Tienda eliminada exitosamente"}

@router.get("/dashboard/", response_model=Store)
async def store_dashboard(current_user: dict = Depends(get_current_active_user)):
    """
    Dashboard de la tienda del usuario
    """
    if current_user["role"] != "store_owner":
        raise HTTPException(status_code=403, detail="Solo store owners pueden ver dashboard")
    
    # Buscar tienda del usuario
    store = db.find_one("stores", {"owner_id": current_user["id"]})
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")
    
    # Métricas de la tienda
    products_count = db.count_documents("products", {"store_id": store["id"]})
    orders_count = db.count_documents("orders", {"store_id": store["id"]})
    total_sales = sum(order["total_price"] for order in db.find("orders", {"store_id": store["id"]}))
    
    # Enriquecer dashboard
    store["metrics"] = {
        "total_products": products_count,
        "total_orders": orders_count,
        "total_sales": float(total_sales),
        "conversion_rate": (orders_count / max(store["views"], 1)) * 100 if store["views"] > 0 else 0
    }
    
    # Productos recientes
    recent_products = db.find("products", {"store_id": store["id"]}, limit=5, sort=[("created_at", -1)])
    store["recent_products"] = recent_products
    
    return store