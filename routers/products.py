from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.product import Product, ProductCreate, ProductUpdate
from crud.product import create_product, get_product, get_products_by_store, update_product, delete_product
from utils.auth import get_current_active_user, verify_role

router = APIRouter()

@router.post("/", response_model=Product)
async def create_new_product(product: ProductCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] not in ["store_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_product(product)
    if not result:
        raise HTTPException(status_code=400, detail="Product creation failed")
    return result

@router.get("/", response_model=List[Product])
async def read_products(skip: int = 0, limit: int = 20):
    # Implement pagination and filtering
    products = db.find("products", {}, limit=limit)
    return products

@router.get("/store/{store_id}", response_model=List[Product])
async def read_products_by_store(store_id: str, skip: int = 0, limit: int = 20):
    products = await get_products_by_store(store_id, skip, limit)
    return products

@router.get("/{product_id}", response_model=Product)
async def read_product(product_id: str):
    product = await get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=Product)
async def update_existing_product(
    product_id: str, product: ProductUpdate, current_user: dict = Depends(get_current_active_user)
):
    product_db = await get_product(product_id)
    if not product_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user["role"] not in ["admin", "store_owner"] or product_db["store_id"] != current_user.get("store_id"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await update_product(product_id, product, product_db["store_id"])
    if not result:
        raise HTTPException(status_code=400, detail="Product update failed")
    return result

@router.delete("/{product_id}")
async def delete_product_endpoint(
    product_id: str, current_user: dict = Depends(get_current_active_user)
):
    product = await get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user["role"] != "admin" and product["store_id"] != current_user.get("store_id"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await delete_product(product_id, product["store_id"])
    if not result:
        raise HTTPException(status_code=400, detail="Product deletion failed")
    return {"message": "Product deleted successfully"}