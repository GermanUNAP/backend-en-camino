from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PaymentMethodEnum(str, Enum):
    card = "card"
    yape = "yape"

class PaymentStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"
    pending_review = "pending_review"
    refunded = "refunded"

class PaymentCreate(BaseModel):
    order_id: str = Field(..., description="ID de la orden asociada")
    amount: Decimal = Field(..., gt=0, description="Monto del pago")
    payment_method: PaymentMethodEnum = Field(..., description="Método de pago")
    token_id: Optional[str] = Field(None, description="Token ID para tarjeta")
    phone: Optional[str] = Field(None, description="Número de teléfono para Yape")
    otp: Optional[str] = Field(None, description="OTP para Yape")
    metadata: Optional[dict] = Field(default_factory=dict, description="Metadatos adicionales")

class Payment(PaymentCreate):
    id: str = Field(..., description="ID único del pago")
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.pending, description="Estado del pago")
    charge_id: Optional[str] = Field(None, description="ID del cargo en Culqi")
    yape_image_url: Optional[str] = Field(None, description="URL del comprobante Yape")
    transaction_id: Optional[str] = Field(None, description="ID de transacción")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")
    refund_reason: Optional[str] = Field(None, description="Razón del reembolso")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "pay_123456789",
                "order_id": "ord_987654321",
                "amount": "25.50",
                "payment_method": "yape",
                "status": "succeeded",
                "charge_id": "ch_abc123def456",
                "yape_image_url": "https://example.com/proof.jpg",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z"
            }
        }