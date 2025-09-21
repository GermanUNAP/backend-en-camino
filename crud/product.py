from database import db
from models.product import ProductCreate, ProductUpdate
from typing import List, Optional

async def create_product(product: ProductCreate) -> Optional[dict]:
    product_dict = product.dict()
    product_dict["views"] = 0
    product_dict["sells_count"] = 0
    product_dict["comments_count"] = 0
    product_dict["average_rating"] = 0.0
    return db.insert_one("products", product_dict)

async def get_product(product_id: str) -> Optional[dict]:
    return db.find_one("products", {"_id": product_id})

async def get_products_by_store(store_id: str, skip: int = 0, limit: int = 20) -> List[dict]:
    return db.find("products", {"store_id": store_id}, limit=limit)

async def update_product(product_id: str, product_update: ProductUpdate, store_id: str) -> Optional[dict]:
    query = {"_id": product_id, "store_id": store_id}
    update_dict = product_update.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    if db.update_one("products", query, update_dict):
        return await get_product(product_id)
    return None

async def delete_product(product_id: str, store_id: str) -> bool:
    query = {"_id": product_id, "store_id": store_id}
    return db.delete_one("products", query)