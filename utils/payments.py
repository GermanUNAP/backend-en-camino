import requests
import hmac
import hashlib
from fastapi import HTTPException
from config import settings
from typing import Dict, Any, Optional
from datetime import datetime

async def process_culqi_payment(
    order_id: str, 
    amount: float, 
    payment_method: str, 
    token_id: Optional[str] = None, 
    phone: Optional[str] = None, 
    otp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Procesar pago con Culqi (tarjeta o Yape)
    """
    headers = {
        "Authorization": f"Bearer {settings.culqi_secret_key}",
        "Content-Type": "application/json",
    }
    
    source_id = None
    
    if payment_method == "card":
        if not token_id:
            raise HTTPException(status_code=400, detail="Token ID required for card payment")
        source_id = token_id
        
    elif payment_method == "yape":
        if not phone or not otp:
            raise HTTPException(status_code=400, detail="Phone number and OTP required for Yape")
        
        # Crear token para Yape
        token_url = "https://api.culqi.com/v1/tokens"
        token_data = {
            "number_phone": phone,
            "otp": otp,
            "amount": int(amount * 100),
            "metadata": {"order_id": order_id}
        }
        
        token_response = requests.post(token_url, headers=headers, json=token_data)
        if token_response.status_code != 201:
            error_detail = token_response.json().get('merchant_message', 'Failed to create Yape token')
            raise HTTPException(status_code=400, detail=error_detail)
        
        token_result = token_response.json()
        source_id = token_result.get("id")
        
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method. Use 'card' or 'yape'")
    
    # Crear cargo con Culqi
    charge_url = "https://api.culqi.com/v1/charges"
    charge_data = {
        "amount": int(amount * 100),
        "currency": "PEN",
        "email": "buyer@example.com",  # Debería venir del usuario
        "source_id": source_id,
        "capture": True,
        "description": f"Pago para orden {order_id}",
        "metadata": {"order_id": order_id, "user_id": "user_id_placeholder"}
    }
    
    response = requests.post(charge_url, headers=headers, json=charge_data)
    
    if response.status_code == 201:
        return response.json()
    else:
        error_detail = response.json().get('merchant_message', 'Payment failed')
        raise HTTPException(status_code=400, detail=error_detail)

async def verify_culqi_webhook(payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
    """
    Verificar firma del webhook de Culqi
    """
    try:
        # Payload como string para HMAC
        payload_string = str(payload)
        expected_signature = hmac.new(
            settings.culqi_secret_key.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        return payload
        
    except Exception as e:
        print(f"Webhook verification error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook verification failed")

def generate_payment_reference(order_id: str) -> str:
    """
    Generar referencia única para pago
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
    return f"PAY-{order_id[:8]}-{timestamp}"

def format_currency(amount: float, currency: str = "PEN") -> str:
    """
    Formatear monto para display
    """
    return f"{amount:.2f} {currency}"