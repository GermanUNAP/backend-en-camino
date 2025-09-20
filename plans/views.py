import requests
from datetime import timedelta
from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SubscriptionPlan, Payment, PlanDefinition
from .serializers import SubscriptionPlanSerializer, PlanDefinitionSerializer, PaymentSerializer
from stores.models import Store

class SubscriptionPlanListView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class PlanDefinitionListView(generics.ListAPIView):
    queryset = PlanDefinition.objects.all()
    serializer_class = PlanDefinitionSerializer
    permission_classes = [IsAuthenticated]

class ProcessSubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        store_id = request.data.get('store_id')
        plan_type = request.data.get('plan_type')
        payment_method = request.data.get('payment_method', 'card')
        try:
            store = Store.objects.get(id=store_id, owner=request.user)
            plan_def = PlanDefinition.objects.get(plan_type=plan_type)
            amount = plan_def.weekly_cost  
            duration_days = 7  

            sub_payment = Payment.objects.create(
                plan_type=plan_type,
                amount=amount,
                payment_date=models.now(),
                end_date=models.now() + timedelta(days=duration_days),
                status='pending',
                currency='PEN'
            )

            headers = {
                "Authorization": f"Bearer {settings.CULQI_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            if payment_method == 'card':
                token_id = request.data.get('token_id')
                source_id = token_id
            elif payment_method == 'yape':
                number_phone = request.data.get('number_phone')
                otp = request.data.get('otp')
                token_url = "https://api.culqi.com/v1/tokens"
                token_data = {
                    "number_phone": number_phone,
                    "otp": otp,
                    "amount": int(amount * 100),
                    "metadata": {"store_id": store_id}
                }
                token_response = requests.post(token_url, headers=headers, json=token_data)
                if token_response.status_code != 201:
                    return Response({'error': 'Failed to create Yape token'}, status=status.HTTP_400_BAD_REQUEST)
                token_result = token_response.json()
                sub_payment.transaction_id = token_result['id']  
                sub_payment.save()
                source_id = token_result['id']
            else:
                return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)

            charge_url = "https://api.culqi.com/v1/charges"
            charge_data = {
                "amount": int(amount * 100),
                "currency": "PEN",
                "email": request.user.email,
                "source_id": source_id,
                "capture": True,
                "description": f"Subscription for {plan_type}",
                "metadata": {"store_id": store_id}
            }
            charge_response = requests.post(charge_url, headers=headers, json=charge_data)
            if charge_response.status_code == 201:
                charge_result = charge_response.json()
                sub_payment.transaction_id = charge_result['id']
                sub_payment.status = 'processing'
                sub_payment.save()
                new_plan = SubscriptionPlan.objects.create(
                    name=plan_def.name,
                    price=amount,
                    currency='PEN',
                    duration_days=duration_days,
                    features=plan_def.description,
                    plan_type=plan_type,
                    start_date=models.now(),
                    end_date=sub_payment.end_date,
                    is_active=True
                )
                if store.payment_history is None:
                    store.payment_history = []
                store.payment_history.append(sub_payment)
                store.current_plan = new_plan
                store.save()
                return Response({'success': True, 'charge_id': charge_result['id']})
            else:
                sub_payment.status = 'failed'
                sub_payment.save()
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)
        except PlanDefinition.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)