from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from payments.models import Payment
from deliveries.models import DeliveryPoint, Shipper
from deliveries.serializers import DeliveryTrackingSerializer

class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(buyer=self.request.user)
        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            payment_method='pending',
            status='pending'
        )
        order.payment = payment
        
        # Create initial tracking event
        from deliveries.models import DeliveryTracking
        DeliveryTracking.objects.create(
            order=order,
            event_type='created',
            responsible_user=self.request.user
        )
        
        # Add to tracking history
        order.tracking_history.append({
            'event_id': 'initial',
            'timestamp': order.created_at.isoformat(),
            'event_type': 'created',
            'user': self.request.user.username,
            'notes': 'Order created'
        })
        order.save()

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Update delivery coordinates if provided
        if 'delivery_latitude' in request.data and 'delivery_longitude' in request.data:
            instance.delivery_latitude = request.data['delivery_latitude']
            instance.delivery_longitude = request.data['delivery_longitude']
            
            # Create geolocation tracking event
            from deliveries.models import DeliveryTracking
            DeliveryTracking.objects.create(
                order=instance,
                event_type='delivery_location_set',
                latitude=instance.delivery_latitude,
                longitude=instance.delivery_longitude,
                location_description=request.data.get('delivery_address', ''),
                responsible_user=request.user,
                notes=f"Delivery coordinates set: {instance.delivery_latitude}, {instance.delivery_longitude}"
            )
            instance.save()

        return Response(serializer.data)

class AssignDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        delivery_point_id = request.data.get('delivery_point_id')
        shipper_id = request.data.get('shipper_id')
        
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)
            
            if delivery_point_id:
                delivery_point = DeliveryPoint.objects.get(id=delivery_point_id)
                order.assigned_delivery_point = delivery_point
                from deliveries.models import DeliveryTracking
                DeliveryTracking.objects.create(
                    order=order,
                    event_type='assigned_to_delivery_point',
                    location_description=delivery_point.address,
                    responsible_user=request.user
                )
            
            if shipper_id:
                shipper = Shipper.objects.get(id=shipper_id)
                order.assigned_shipper = shipper
                from deliveries.models import DeliveryTracking
                DeliveryTracking.objects.create(
                    order=order,
                    event_type='assigned_to_shipper',
                    location_description=shipper.current_location,
                    responsible_user=request.user
                )
                shipper.assigned_orders.add(order)
                shipper.save()
            
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
            
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        except DeliveryPoint.DoesNotExist:
            return Response({'error': 'Delivery point not found'}, status=404)
        except Shipper.DoesNotExist:
            return Response({'error': 'Shipper not found'}, status=404)

class OrderTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if request.user.role != 'admin' and order.buyer != request.user and order.store.owner != request.user:
                return Response({'error': 'Permission denied'}, status=403)
            
            from deliveries.models import DeliveryTracking
            tracking_events = DeliveryTracking.objects.filter(order=order).order_by('timestamp')
            serializer = DeliveryTrackingSerializer(tracking_events, many=True)
            return Response({
                'order': OrderSerializer(order).data,
                'tracking_events': serializer.data,
                'tracking_history': order.tracking_history
            })
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == "admin":
            orders = Order.objects.all()
        elif request.user.role == "store_owner":
            orders = Order.objects.filter(store__owner=request.user)
        elif request.user.role == "shipper":
            shipper = Shipper.objects.filter(user=request.user).first()
            if shipper:
                orders = shipper.assigned_orders.all()
            else:
                orders = Order.objects.none()
        elif request.user.role == "delivery_point":
            delivery_point = DeliveryPoint.objects.filter(user=request.user).first()
            if delivery_point:
                orders = delivery_point.assigned_orders.all()
            else:
                orders = Order.objects.none()
        else:
            orders = request.user.orders.all()
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)