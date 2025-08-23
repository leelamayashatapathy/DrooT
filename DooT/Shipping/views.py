from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import ShippingZone, ShippingMethod, ShippingRate, Shipment, ShipmentTracking, Address
from .serializers import (
    ShippingZoneSerializer, ShippingMethodSerializer, ShippingRateSerializer,
    ShipmentSerializer, ShipmentCreateSerializer, ShipmentUpdateSerializer,
    AddressSerializer, AddressCreateSerializer, ShippingCalculatorSerializer
)

# Keep generics for simple listing and retrieval
class ShippingZoneListView(generics.ListAPIView):
    queryset = ShippingZone.objects.filter(is_active=True)
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.AllowAny]

class ShippingZoneDetailView(generics.RetrieveAPIView):
    queryset = ShippingZone.objects.filter(is_active=True)
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.AllowAny]

class ShippingMethodListView(generics.ListAPIView):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]

class ShippingMethodDetailView(generics.RetrieveAPIView):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]

class ShippingRateListView(generics.ListAPIView):
    serializer_class = ShippingRateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shipping_zone', 'shipping_method', 'is_active']
    ordering_fields = ['base_rate', 'weight_rate']
    ordering = ['base_rate']

class AddressListView(generics.ListAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['address_type', 'is_default']
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressDetailView(generics.RetrieveAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

# Convert to APIView for custom operations
class AddressCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create address with custom validation"""
        serializer = AddressCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check if this is the first address (make it default)
                if not Address.objects.filter(user=request.user).exists():
                    serializer.validated_data['is_default'] = True
                
                # If setting as default, unset other defaults
                if serializer.validated_data.get('is_default', False):
                    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                
                address = serializer.save()
                
                return Response({
                    'message': 'Address created successfully',
                    'address': AddressSerializer(address).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating address: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get address and check ownership"""
        try:
            return Address.objects.get(id=pk, user=self.request.user)
        except Address.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update address with custom logic"""
        address = self.get_object(pk)
        if not address:
            return Response({'error': 'Address not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # If setting as default, unset other defaults
                if serializer.validated_data.get('is_default', False):
                    Address.objects.filter(user=request.user, is_default=True).exclude(id=pk).update(is_default=False)
                
                serializer.save()
                
                return Response({
                    'message': 'Address updated successfully',
                    'address': AddressSerializer(address).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating address: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete address with custom logic"""
        address = self.get_object(pk)
        if not address:
            return Response({'error': 'Address not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # If this was the default address, set another one as default
            if address.is_default:
                other_address = Address.objects.filter(user=request.user).exclude(id=pk).first()
                if other_address:
                    other_address.is_default = True
                    other_address.save()
            
            address.delete()
            
            return Response({'message': 'Address deleted successfully'})
            
        except Exception as e:
            return Response({
                'error': f'Error deleting address: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShipmentListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'carrier', 'order']
    ordering_fields = ['created_at', 'estimated_delivery']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            # Seller view - show shipments for their orders
            return Shipment.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            # Customer view - show their own shipments
            return Shipment.objects.filter(order__user=self.request.user)

class ShipmentDetailView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return Shipment.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return Shipment.objects.filter(order__user=self.request.user)

class ShipmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create shipment with custom validation"""
        serializer = ShipmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                order = serializer.validated_data.get('order')
                
                # Check if user has access to this order
                if hasattr(request.user, 'seller_profile'):
                    if order.seller != request.user.seller_profile:
                        return Response({
                            'error': 'You can only create shipments for your own orders'
                        }, status=status.HTTP_403_FORBIDDEN)
                else:
                    if order.user != request.user:
                        return Response({
                            'error': 'You can only create shipments for your own orders'
                        }, status=status.HTTP_403_FORBIDDEN)
                
                # Check if shipment already exists
                if Shipment.objects.filter(order=order).exists():
                    return Response({
                        'error': 'Shipment already exists for this order'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create shipment
                shipment = serializer.save()
                
                # Create initial tracking event
                ShipmentTracking.objects.create(
                    shipment=shipment,
                    status='created',
                    location='Origin',
                    notes='Shipment created and ready for pickup'
                )
                
                return Response({
                    'message': 'Shipment created successfully',
                    'shipment': ShipmentSerializer(shipment).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating shipment: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShipmentUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get shipment and check access"""
        try:
            if hasattr(self.request.user, 'seller_profile'):
                return Shipment.objects.get(id=pk, order__seller=self.request.user.seller_profile)
            else:
                return Shipment.objects.get(id=pk, order__user=self.request.user)
        except Shipment.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update shipment with custom logic"""
        shipment = self.get_object(pk)
        if not shipment:
            return Response({'error': 'Shipment not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShipmentUpdateSerializer(shipment, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Track status changes
                old_status = shipment.status
                new_status = serializer.validated_data.get('status')
                
                serializer.save()
                
                # Create tracking event if status changed
                if new_status and new_status != old_status:
                    tracking_notes = serializer.validated_data.get('notes', f'Status updated to {new_status}')
                    ShipmentTracking.objects.create(
                        shipment=shipment,
                        status=new_status,
                        location=serializer.validated_data.get('location', 'In Transit'),
                        notes=tracking_notes
                    )
                
                return Response({
                    'message': 'Shipment updated successfully',
                    'shipment': ShipmentSerializer(shipment).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating shipment: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShipmentTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, shipment_id):
        """Get shipment tracking information"""
        try:
            if hasattr(request.user, 'seller_profile'):
                shipment = Shipment.objects.get(
                    id=shipment_id,
                    order__seller=request.user.seller_profile
                )
            else:
                shipment = Shipment.objects.get(
                    id=shipment_id,
                    order__user=request.user
                )
            
            tracking_events = ShipmentTracking.objects.filter(shipment=shipment).order_by('created_at')
            
            return Response({
                'shipment_id': shipment.shipment_id,
                'order_number': shipment.order.order_number,
                'carrier': shipment.carrier,
                'tracking_number': shipment.tracking_number,
                'current_status': shipment.status,
                'estimated_delivery': shipment.estimated_delivery,
                'tracking_events': [
                    {
                        'status': event.status,
                        'location': event.location,
                        'notes': event.notes,
                        'timestamp': event.created_at
                    }
                    for event in tracking_events
                ]
            })
            
        except Shipment.DoesNotExist:
            return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error retrieving tracking info: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShippingCalculatorView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Calculate shipping rates with custom logic"""
        serializer = ShippingCalculatorSerializer(data=request.data)
        if serializer.is_valid():
            try:
                origin_country = serializer.validated_data['origin_country']
                destination_country = serializer.validated_data['destination_country']
                package_weight = serializer.validated_data['package_weight']
                item_count = serializer.validated_data['item_count']
                order_value = serializer.validated_data['order_value']
                
                # Find applicable shipping zones
                shipping_zones = ShippingZone.objects.filter(
                    countries__icontains=destination_country,
                    is_active=True
                )
                
                available_rates = []
                
                for zone in shipping_zones:
                    rates = ShippingRate.objects.filter(
                        shipping_zone=zone,
                        is_active=True
                    )
                    
                    for rate in rates:
                        # Calculate shipping cost
                        shipping_cost = self._calculate_shipping_cost(
                            rate, package_weight, item_count, order_value
                        )
                        
                        if shipping_cost > 0:
                            available_rates.append({
                                'method': rate.shipping_method.name,
                                'carrier': rate.shipping_method.carrier,
                                'estimated_days': rate.estimated_days,
                                'base_cost': rate.base_rate,
                                'total_cost': shipping_cost,
                                'zone': zone.name
                            })
                
                # Sort by cost and delivery time
                available_rates.sort(key=lambda x: (x['total_cost'], x['estimated_days']))
                
                return Response({
                    'origin': origin_country,
                    'destination': destination_country,
                    'package_weight': package_weight,
                    'item_count': item_count,
                    'order_value': order_value,
                    'available_rates': available_rates
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error calculating shipping: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_shipping_cost(self, rate, weight, item_count, order_value):
        """Calculate shipping cost based on rate structure"""
        cost = rate.base_rate
        
        # Add weight-based cost
        if weight > rate.weight_threshold:
            extra_weight = weight - rate.weight_threshold
            cost += extra_weight * rate.weight_rate
        
        # Add item-based cost
        if item_count > 1:
            cost += (item_count - 1) * rate.item_rate
        
        # Add value-based cost for high-value orders
        if order_value > rate.value_threshold:
            cost += (order_value - rate.value_threshold) * rate.value_rate
        
        return round(cost, 2)

# Admin shipping management
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_shipping_rates(request):
    """Update shipping rates (admin only)"""
    try:
        zone_id = request.data.get('zone_id')
        method_id = request.data.get('method_id')
        new_base_rate = request.data.get('base_rate')
        
        if not all([zone_id, method_id, new_base_rate]):
            return Response({
                'error': 'zone_id, method_id, and base_rate are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rate = ShippingRate.objects.get(
            shipping_zone_id=zone_id,
            shipping_method_id=method_id
        )
        
        rate.base_rate = new_base_rate
        rate.save()
        
        return Response({
            'message': 'Shipping rate updated successfully',
            'rate': ShippingRateSerializer(rate).data
        })
        
    except ShippingRate.DoesNotExist:
        return Response({'error': 'Shipping rate not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error updating shipping rate: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def shipping_statistics(request):
    """Get shipping statistics for admin dashboard"""
    try:
        total_shipments = Shipment.objects.count()
        pending_shipments = Shipment.objects.filter(status='pending').count()
        in_transit = Shipment.objects.filter(status='in_transit').count()
        delivered = Shipment.objects.filter(status='delivered').count()
        
        # Calculate average delivery time
        delivered_shipments = Shipment.objects.filter(
            status='delivered',
            delivered_at__isnull=False
        )
        
        avg_delivery_time = 0
        if delivered_shipments.exists():
            total_time = sum([
                (shipment.delivered_at - shipment.created_at).days
                for shipment in delivered_shipments
            ])
            avg_delivery_time = total_time / delivered_shipments.count()
        
        return Response({
            'total_shipments': total_shipments,
            'pending_shipments': pending_shipments,
            'in_transit': in_transit,
            'delivered': delivered,
            'average_delivery_time_days': round(avg_delivery_time, 1)
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
