from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import DeliveryPoint, Shipper, DeliveryTracking
from .serializers import DeliveryPointSerializer, ShipperSerializer, DeliveryTrackingSerializer
from orders.serializers import OrderSerializer
from orders.models import Order

class DeliveryPointListView(generics.ListCreateAPIView):
    queryset = DeliveryPoint.objects.all()
    serializer_class = DeliveryPointSerializer
    permission_classes = [IsAuthenticated]

class DeliveryPointDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeliveryPoint.objects.all()
    serializer_class = DeliveryPointSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class DeliveryPointOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        delivery_point = DeliveryPoint.objects.get(id=pk)
        orders = delivery_point.assigned_orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ShipperListView(generics.ListCreateAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    permission_classes = [IsAuthenticated]

class ShipperDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class ShipperDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == "shipper":
            shipper = Shipper.objects.filter(user=request.user).first()
            if shipper:
                orders = shipper.assigned_orders.all()
                serializer = OrderSerializer(orders, many=True)
                return Response(serializer.data)
        return Response([])

class UpdateShipperLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != "shipper":
            return Response({'error': 'Only shippers can update location'}, status=403)
        
        shipper = Shipper.objects.get(id=pk, user=request.user)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        current_location = request.data.get('current_location', '')
        
        if latitude and longitude:
            shipper.latitude = float(latitude)
            shipper.longitude = float(longitude)
            shipper.current_location = current_location
            shipper.save()
            
            # Update tracking for all assigned orders
            for order in shipper.assigned_orders.filter(status__in=['shipped', 'out_for_delivery']):
                tracking_event = DeliveryTracking.objects.create(
                    order=order,
                    event_type='in_transit',
                    latitude=shipper.latitude,
                    longitude=shipper.longitude,
                    location_description=current_location,
                    responsible_user=request.user
                )
                order.tracking_history.append({
                    'event_id': str(tracking_event.id),
                    'timestamp': tracking_event.timestamp.isoformat(),
                    'event_type': tracking_event.event_type,
                    'latitude': tracking_event.latitude,
                    'longitude': tracking_event.longitude,
                    'location': tracking_event.location_description
                })
                order.save()
            
            return Response({'success': True, 'location': {
                'latitude': shipper.latitude,
                'longitude': shipper.longitude,
                'address': current_location
            }})
        return Response({'error': 'Latitude and longitude required'}, status=400)

class CreateTrackingEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        event_type = request.data.get('event_type')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location_description = request.data.get('location_description', '')
        notes = request.data.get('notes', '')
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Validate permissions based on event type
            if event_type in ['picked_up', 'in_transit', 'out_for_delivery', 'delivered']:
                if request.user.role != 'shipper' or order.assigned_shipper.user != request.user:
                    return Response({'error': 'Permission denied'}, status=403)
            elif event_type in ['assigned_to_delivery_point', 'arrived_at_delivery_point']:
                if request.user.role != 'delivery_point' or order.assigned_delivery_point.user != request.user:
                    return Response({'error': 'Permission denied'}, status=403)
            
            tracking_event = DeliveryTracking.objects.create(
                order=order,
                event_type=event_type,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                location_description=location_description,
                responsible_user=request.user,
                notes=notes
            )
            
            # Update order status based on event
            status_mapping = {
                'payment_confirmed': 'processing',
                'picked_up': 'shipped',
                'in_transit': 'shipped',
                'out_for_delivery': 'shipped',
                'delivered': 'delivered',
                'cancelled': 'cancelled'
            }
            
            if event_type in status_mapping:
                order.status = status_mapping[event_type]
                if event_type == 'delivered':
                    order.actual_delivery_time = tracking_event.timestamp
                    shipper = order.assigned_shipper
                    if shipper:
                        shipper.total_deliveries += 1
                        shipper.successful_deliveries += 1
                        shipper.save()
                order.save()
            
            # Update tracking history
            order.tracking_history.append({
                'event_id': str(tracking_event.id),
                'timestamp': tracking_event.timestamp.isoformat(),
                'event_type': tracking_event.event_type,
                'latitude': tracking_event.latitude,
                'longitude': tracking_event.longitude,
                'location': tracking_event.location_description,
                'user': request.user.username,
                'notes': notes
            })
            order.save()
            
            serializer = DeliveryTrackingSerializer(tracking_event)
            return Response(serializer.data)
            
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)