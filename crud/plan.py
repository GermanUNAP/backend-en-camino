from database import db
from models.plan import PlanDefinitionCreate, PaymentCreate, SubscriptionPlan, PlanDefinition, Payment
from typing import List, Optional
from datetime import datetime, timedelta

async def create_plan_definition(plan: PlanDefinitionCreate) -> Optional[dict]:
    plan_dict = plan.dict()
    return db.insert_one("plan_definitions", plan_dict)

async def get_plan_definitions() -> List[dict]:
    return db.find("plan_definitions", {})

async def create_subscription(store_id: str, plan_type: str, amount: float) -> Optional[dict]:
    definition = db.find_one("plan_definitions", {"plan_type": plan_type})
    if not definition:
        return None
    duration_days = 7  # Weekly
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    plan_dict = {
        "name": definition["name"],
        "price": amount,
        "currency": "PEN",
        "duration_days": duration_days,
        "features": definition["description"],
        "plan_type": plan_type,
        "start_date": start_date,
        "end_date": end_date,
        "is_active": True,
        "store_id": store_id
    }
    result = db.insert_one("subscription_plans", plan_dict)
    if result:
        db.update_one("stores", {"_id": store_id}, {"current_plan": result})
    return result

async def add_payment_to_store(store_id: str, payment: PaymentCreate) -> Optional[dict]:
    query = {"_id": store_id}
    payment_dict = payment.dict()
    payment_dict["payment_date"] = datetime.utcnow()
    payment_dict["end_date"] = payment.payment_date + timedelta(days=7)  # Example
    result = db.update_one("stores", query, {"$push": {"payment_history": payment_dict}})
    if result:
        # Update subscription end date
        db.update_one("subscription_plans", {"store_id": store_id}, {"end_date": payment_dict["end_date"]})
    return payment_dict if result else None

async def get_subscription_plans(store_id: str) -> List[dict]:
    return db.find("subscription_plans", {"store_id": store_id})