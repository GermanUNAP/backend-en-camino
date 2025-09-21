from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional  # ← ESTA LÍNEA ERA LA FALTANTE
from models.payment import PaymentCreate, Payment
from crud.payment import create_payment, get_payment, get_payments_by_user, handle_culqi_webhook
from utils.auth import get_current_active_user
from utils.payments import verify_culqi_webhook
from database import db
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.post("/process/", response_model=Payment)
async def process_payment_endpoint(
    payment: PaymentCreate, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Procesar pago con Culqi (tarjeta o Yape)
    """
    if current_user["role"] not in ["buyer", "store_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await create_payment(payment, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Payment processing failed")
    
    return result

@router.get("/{payment_id}", response_model=Payment)
async def get_payment_detail(payment_id: str, current_user: dict = Depends(get_current_active_user)):
    """
    Obtener detalle de un pago
    """
    payment = await get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if current_user["role"] != "admin" and payment["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return payment

@router.get("/", response_model=List[Payment])
async def get_user_payments(skip: int = 0, limit: int = 20, current_user: dict = Depends(get_current_active_user)):
    """
    Obtener pagos del usuario (dashboard)
    """
    payments = await get_payments_by_user(current_user["id"], skip, limit)
    return payments

@router.get("/dashboard/", response_model=List[Payment])
async def payment_dashboard(current_user: dict = Depends(get_current_active_user)):
    """
    Dashboard completo de pagos con órdenes relacionadas
    """
    payments = await get_payments_by_user(current_user["id"])
    
    # Enriquecer cada pago con info de la orden
    enriched_payments = []
    for payment in payments:
        if payment.get("order_id"):
            order = db.find_one("orders", {"_id": payment["order_id"]})
            if order:
                payment["order_info"] = {
                    "id": order["id"],
                    "total_price": str(order["total_price"]),
                    "status": order["status"],
                    "delivery_address": order.get("delivery_address", ""),
                    "created_at": order["created_at"]
                }
        enriched_payments.append(payment)
    
    return enriched_payments

@router.post("/webhooks/culqi/")
async def culqi_webhook_handler(payload: Dict[str, Any]):
    """
    Webhook de Culqi para actualizar estado de pagos automáticamente
    """
    try:
        # Verificar firma del webhook (en producción)
        # signature = request.headers.get("Culqi-Signature")
        # await verify_culqi_webhook(payload, signature)
        
        result = await handle_culqi_webhook(payload)
        if result.get("status") == "success":
            return {"status": "ok", "message": "Webhook processed successfully"}
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Webhook processing failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/yape/proof/")
async def upload_yape_proof_endpoint(
    payment_id: str, 
    image_url: str, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Subir comprobante de pago manual Yape
    """
    from crud.payment import upload_yape_proof
    
    result = await upload_yape_proof(payment_id, image_url, current_user["id"])
    if not result:
        raise HTTPException(status_code=400, detail="Failed to upload Yape proof")
    
    return {
        "message": "Yape proof uploaded successfully", 
        "payment_id": payment_id, 
        "image_url": image_url
    }

@router.put("/{payment_id}/status")
async def update_payment_status_endpoint(
    payment_id: str, 
    status: str, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualizar estado de pago manualmente (admin)
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    from crud.payment import update_payment_status
    
    result = await update_payment_status(payment_id, status)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to update payment status")
    
    return {"message": f"Payment status updated to {status}"}

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str, 
    current_user: dict = Depends(get_current_active_user)
):
    """
    Eliminar pago (solo admin)
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    result = db.delete_one("payments", {"_id": payment_id})
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {"message": "Payment deleted successfully"}