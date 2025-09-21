from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.plan import PlanDefinition, PlanDefinitionCreate, SubscriptionPlan, Payment, PaymentCreate
from crud.plan import create_plan_definition, get_plan_definitions, create_subscription, add_payment_to_store, get_subscription_plans
from utils.auth import get_current_active_user
from utils.payments import process_culqi_payment

router = APIRouter()

@router.post("/definitions/", response_model=PlanDefinition)
async def create_new_plan_definition(plan: PlanDefinitionCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_plan_definition(plan)
    if not result:
        raise HTTPException(status_code=400, detail="Plan definition creation failed")
    return result

@router.get("/definitions/", response_model=List[PlanDefinition])
async def read_plan_definitions():
    return await get_plan_definitions()

@router.post("/subscriptions/", response_model=SubscriptionPlan)
async def create_new_subscription(store_id: str, plan_type: str, amount: float, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "store_owner" or current_user["store_id"] != store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await create_subscription(store_id, plan_type, amount)
    if not result:
        raise HTTPException(status_code=400, detail="Subscription creation failed")
    return result

@router.post("/payments/", response_model=Payment)
async def create_payment(payment: PaymentCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "store_owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    culqi_result = await process_culqi_payment(
        order_id=payment.id,  # Use payment id as reference
        amount=float(payment.amount),
        payment_method=payment.payment_method,
        token_id=payment.token_id,
        phone=payment.phone,
        otp=payment.otp
    )
    payment_dict = payment.dict()
    payment_dict["status"] = "processing" if culqi_result.get("amount_status") == "pending" else "completed"
    payment_dict["transaction_id"] = culqi_result.get("id")
    result = await add_payment_to_store(current_user["store_id"], payment_dict)
    if not result:
        raise HTTPException(status_code=400, detail="Payment creation failed")
    return payment_dict

@router.get("/subscriptions/", response_model=List[SubscriptionPlan])
async def read_subscriptions(store_id: str, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "admin" and current_user["store_id"] != store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await get_subscription_plans(store_id)