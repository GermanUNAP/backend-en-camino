from database import db
from models.payment import PaymentCreate, Payment
from models.order import OrderStatusEnum
from utils.payments import process_culqi_payment
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

async def create_payment(payment: PaymentCreate, user_id: str) -> Optional[dict]:
    """
    Crear y procesar un pago con Culqi
    """
    try:
        # Procesar pago con Culqi
        culqi_result = await process_culqi_payment(
            order_id=payment.order_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method,
            token_id=payment.token_id,
            phone=getattr(payment, 'phone', None),
            otp=getattr(payment, 'otp', None)
        )
        
        # Preparar documento de pago
        payment_dict = payment.dict()
        payment_dict["user_id"] = user_id
        payment_dict["status"] = "processing" if culqi_result.get("amount_status") == "pending" else "succeeded"
        payment_dict["charge_id"] = culqi_result.get("id")
        payment_dict["metadata"] = culqi_result.get("metadata", {})
        payment_dict["created_at"] = datetime.utcnow()
        payment_dict["updated_at"] = datetime.utcnow()
        
        # Insertar pago en MongoDB
        result = db.insert_one("payments", payment_dict)
        
        if result:
            # Actualizar estado de la orden a "paid"
            order_update = {
                "status": OrderStatusEnum.paid,
                "payment_id": result["id"],
                "updated_at": datetime.utcnow()
            }
            db.update_one("orders", {"_id": payment.order_id}, order_update)
            
            # Crear evento de tracking para la orden
            tracking_event = {
                "event_type": "payment_confirmed",
                "timestamp": datetime.utcnow(),
                "notes": f"Pago procesado exitosamente - Charge ID: {culqi_result.get('id')}",
                "responsible_user_id": user_id
            }
            db.update_one("orders", {"_id": payment.order_id}, {"$push": {"tracking_history": tracking_event}})
        
        return result
        
    except HTTPException as e:
        # Errores de validación de FastAPI
        raise e
    except Exception as e:
        # Errores de Culqi o conexión
        print(f"Payment error: {str(e)}")
        # Crear pago fallido
        payment_dict = payment.dict()
        payment_dict["user_id"] = user_id
        payment_dict["status"] = "failed"
        payment_dict["error_message"] = str(e)
        payment_dict["created_at"] = datetime.utcnow()
        payment_dict["updated_at"] = datetime.utcnow()
        failed_payment = db.insert_one("payments", payment_dict)
        return failed_payment

async def get_payment(payment_id: str) -> Optional[dict]:
    """Obtener pago por ID"""
    return db.find_one("payments", {"_id": payment_id})

async def get_payments_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[dict]:
    """Obtener pagos de un usuario"""
    return db.find("payments", {"user_id": user_id}, limit=limit)

async def get_payments_by_order(order_id: str) -> Optional[dict]:
    """Obtener pago de una orden específica"""
    return db.find_one("payments", {"order_id": order_id})

async def update_payment_status(payment_id: str, status: str, user_id: str = None) -> bool:
    """Actualizar estado de pago (para webhooks)"""
    query = {"_id": payment_id}
    if user_id:
        query["user_id"] = user_id
        
    update = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    result = db.update_one("payments", query, update)
    
    if result and status == "succeeded":
        # Actualizar orden si el pago es exitoso
        payment = await get_payment(payment_id)
        if payment and payment.get("order_id"):
            order_update = {
                "status": OrderStatusEnum.paid,
                "payment_id": payment_id,
                "updated_at": datetime.utcnow()
            }
            db.update_one("orders", {"_id": payment["order_id"]}, order_update)
            
            # Crear evento de tracking
            tracking_event = {
                "event_type": "payment_confirmed",
                "timestamp": datetime.utcnow(),
                "notes": f"Pago confirmado exitosamente",
                "responsible_user_id": "system"
            }
            db.update_one("orders", {"_id": payment["order_id"]}, {"$push": {"tracking_history": tracking_event}})
    
    return result

async def upload_yape_proof(payment_id: str, image_url: str, user_id: str) -> bool:
    """Subir comprobante de pago Yape"""
    query = {"_id": payment_id, "user_id": user_id}
    update = {
        "yape_image_url": image_url,
        "updated_at": datetime.utcnow(),
        "status": "pending_review"  # Cambiar a revisión manual
    }
    return db.update_one("payments", query, update)

async def handle_culqi_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manejar webhook de Culqi
    """
    try:
        if payload.get("object") == "Charge":
            charge = payload.get("data", {}).get("object", {})
            charge_id = charge.get("id")
            action = charge.get("action")
            
            if not charge_id:
                return {"status": "error", "message": "No charge ID in payload"}
            
            # Buscar pago relacionado
            payment = db.find_one("payments", {"charge_id": charge_id})
            if not payment:
                print(f"Payment not found for charge {charge_id}")
                return {"status": "ignored", "message": "Payment not found"}
            
            # Actualizar estado según el evento
            if action == "charge.succeeded":
                success = await update_payment_status(payment["id"], "succeeded")
                if success:
                    print(f"Payment {payment['id']} marked as succeeded")
                else:
                    print(f"Failed to update payment {payment['id']} to succeeded")
                    
            elif action == "charge.rejected":
                rejected = await update_payment_status(payment["id"], "failed")
                if rejected:
                    print(f"Payment {payment['id']} marked as failed")
                else:
                    print(f"Failed to update payment {payment['id']} to failed")
            
            return {"status": "success", "payment_id": payment["id"], "action": action}
            
        return {"status": "ignored", "message": "Not a charge event"}
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

async def get_payment_dashboard(user_id: str) -> List[dict]:
    """Dashboard de pagos para usuario/tienda"""
    payments = await get_payments_by_user(user_id)
    
    # Enriquecer con información de órdenes
    for payment in payments:
        if payment.get("order_id"):
            order = db.find_one("orders", {"_id": payment["order_id"]})
            if order:
                payment["order"] = {
                    "id": order["id"],
                    "total_price": order["total_price"],
                    "status": order["status"],
                    "delivery_address": order["delivery_address"]
                }
    
    return payments

async def refund_payment(payment_id: str, user_id: str, reason: str) -> bool:
    """Procesar reembolso de pago"""
    payment = await get_payment(payment_id)
    if not payment or payment["user_id"] != user_id:
        return False
    
    if payment["status"] != "succeeded":
        return False
    
    # Llamada a Culqi para reembolso (implementar según docs)
    try:
        headers = {
            "Authorization": f"Bearer {settings.culqi_secret_key}",
            "Content-Type": "application/json",
        }
        refund_data = {
            "amount": int(float(payment["amount"]) * 100),
            "reason": reason
        }
        response = requests.post(
            f"https://api.culqi.com/v1/refunds/{payment['charge_id']}",
            headers=headers,
            json=refund_data
        )
        
        if response.status_code == 201:
            # Marcar como reembolsado
            db.update_one("payments", {"_id": payment_id}, {
                "status": "refunded",
                "refund_reason": reason,
                "updated_at": datetime.utcnow()
            })
            
            # Actualizar orden
            if payment.get("order_id"):
                db.update_one("orders", {"_id": payment["order_id"]}, {
                    "status": "refunded",
                    "updated_at": datetime.utcnow()
                })
            
            return True
        else:
            print(f"Refund failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Refund error: {str(e)}")
        return False