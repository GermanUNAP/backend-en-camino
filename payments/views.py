import requests
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
from django.core.files.storage import default_storage

@method_decorator(csrf_exempt, name='dispatch')
class CulqiWebhookView(APIView):
    def post(self, request):
        signature = request.headers.get('Culqi-Signature')
        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=400)
        expected_signature = hmac.new(
            settings.CULQI_SECRET_KEY.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        event = request.data
        if event.get('object') == 'Charge':
            charge = event.get('data', {}).get('object', {})
            charge_id = charge.get('id')
            try:
                payment = Payment.objects.get(charge_id=charge_id)
                action = charge.get('action')
                if action == 'charge.succeeded':
                    payment.status = 'succeeded'
                    payment.order.status = 'paid'
                elif action == 'charge.rejected':
                    payment.status = 'failed'
                    payment.order.status = 'cancelled'
                payment.save()
                payment.order.save()
            except Payment.DoesNotExist:
                pass
        return JsonResponse({'status': 'ok'})

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'card')
        try:
            order = Order.objects.get(id=order_id, buyer=request.user, status='pending')
            payment = order.payment
            if payment.status != 'pending':
                return Response({'error': 'Payment already processed'}, status=status.HTTP_400_BAD_REQUEST)
            payment.payment_method = payment_method
            payment.save()

            headers = {
                "Authorization": f"Bearer {settings.CULQI_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            if payment_method == 'card':
                token_id = request.data.get('token_id')
                if not token_id:
                    return Response({'error': 'Token ID required for card'}, status=status.HTTP_400_BAD_REQUEST)
                payment.token_id = token_id
                payment.save()
                source_id = token_id
            elif payment_method == 'yape':
                number_phone = request.data.get('number_phone')
                otp = request.data.get('otp')
                if not number_phone or not otp:
                    return Response({'error': 'Phone number and OTP required for Yape'}, status=status.HTTP_400_BAD_REQUEST)
                token_url = "https://api.culqi.com/v1/tokens"
                token_data = {
                    "number_phone": number_phone,
                    "otp": otp,
                    "amount": int(order.total_price * 100),
                    "metadata": {"order_id": order_id}
                }
                token_response = requests.post(token_url, headers=headers, json=token_data)
                if token_response.status_code != 201:
                    return Response({'error': token_response.json().get('merchant_message', 'Failed to create Yape token')}, status=status.HTTP_400_BAD_REQUEST)
                token_result = token_response.json()
                payment.token_id = token_result['id']
                payment.save()
                source_id = token_result['id']
            else:
                return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)

            charge_url = "https://api.culqi.com/v1/charges"
            charge_data = {
                "amount": int(order.total_price * 100),
                "currency": "PEN",
                "email": request.user.email,
                "source_id": source_id,
                "capture": True,
                "description": f"Order {order.id}",
                "metadata": {"order_id": order_id}
            }
            charge_response = requests.post(charge_url, headers=headers, json=charge_data)
            if charge_response.status_code == 201:
                charge_result = charge_response.json()
                payment.charge_id = charge_result['id']
                payment.status = 'processing'
                payment.save()
                return Response({
                    'success': True,
                    'charge_id': charge_result['id'],
                    'status': charge_result.get('amount_status')
                })
            else:
                payment.status = 'failed'
                payment.save()
                return Response({
                    'success': False,
                    'error': charge_response.json().get('merchant_message', 'Payment failed')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadYapeProofView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        file = request.FILES.get('file')
        if not payment_id or not file:
            return Response({'error': 'Payment ID and file required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(id=payment_id, order__buyer=request.user)
            if payment.payment_method != 'yape':
                return Response({'error': 'Not a Yape payment'}, status=status.HTTP_400_BAD_REQUEST)
            file_path = f"payments/yape/{payment_id}/{file.name}"
            url = default_storage.save(file_path, file)
            payment.yape_image_url = default_storage.url(url)
            payment.save()
            return Response({'success': True, 'yape_image_url': payment.yape_image_url})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)