from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PlanTypeEnum(str, Enum):
    freemium = "freemium"
    crece = "crece"
    pro_plus = "pro+"
    empresa = "empresa"

class PaymentStatusEnum(str, Enum):
    completed = "completed"
    pending = "pending"
    failed = "failed"

class Payment(BaseModel):
    id: Optional[str] = None
    plan_type: PlanTypeEnum
    amount: Decimal
    payment_date: datetime
    end_date: datetime
    transaction_id: Optional[str] = None
    discount_applied_for_weeks: int = 0
    status: PaymentStatusEnum = PaymentStatusEnum.pending
    currency: str = "PEN"
    yape_image_url: Optional[str] = None

class PaymentCreate(Payment):
    plan_id: Optional[str] = None

class PlanDefinitionCreate(BaseModel):
    name: str
    weekly_cost: Decimal
    monthly_cost: Optional[Decimal] = None
    description: List[str]
    plan_type: PlanTypeEnum

class PlanDefinition(PlanDefinitionCreate):
    id: str

class SubscriptionPlan(BaseModel):
    id: Optional[str] = None
    name: str
    price: Decimal
    currency: str = "PEN"
    duration_days: int
    features: List[str]
    plan_type: PlanTypeEnum
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    discount_end_date: Optional[datetime] = None