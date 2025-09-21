from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
from typing import Optional, Dict, Any, List

class Database:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[settings.mongo_uri.split('/')[-1]]  # Extrae DB name
            print("✅ Connected to GaussDB NoSQL")
        except ConnectionFailure as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            document['_id'] = str(result.inserted_id)
            return document
        except Exception as e:
            print(f"Error inserting document: {e}")
            return None

    def find_one(self, collection_name: str, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(query, projection)
            if result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error finding document: {e}")
            return None

    def find(self, collection_name: str, query: Dict[str, Any] = {}, projection: Optional[Dict[str, Any]] = None, limit: int = 0) -> List[Dict[str, Any]]:
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query, projection)
            if limit:
                cursor = cursor.limit(limit)
            results = list(cursor)
            for result in results:
                result['_id'] = str(result['_id'])
            return results
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, {'$set': update})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

db = Database()