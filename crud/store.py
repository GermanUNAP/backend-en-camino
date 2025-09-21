from database import db
from models.store import StoreCreate, StoreUpdate
from typing import List

async def create_store(store: StoreCreate) -> dict:
    return db.insert_one("stores", store.dict())

async def get_store(store_id: str) -> dict:
    return db.find_one("stores", {"_id": store_id})

async def get_stores(skip: int = 0, limit: int = 20) -> List[dict]:
    query = {}
    return db.find("stores", query, limit=limit)

async def update_store(store_id: str, store: StoreUpdate) -> bool:
    return db.update_one("stores", {"_id": store_id}, store.dict(exclude_unset=True))

async def delete_store(store_id: str) -> bool:
    return db.delete_one("stores", {"_id": store_id})