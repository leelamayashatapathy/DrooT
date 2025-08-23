from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from .models import Cart, CartItem, Order, OrderItem, OrderStatus, ReturnRequest
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, ReturnRequestSerializer, ReturnRequestUpdateSerializer,
    CartItemUpdateSerializer, CartCheckoutSerializer
)

# Keep generics for simple listing and retrieval
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'seller']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            # Seller view - show orders for their products
            return Order.objects.filter(seller=self.request.user.seller_profile)
        else:
            # Customer view - show their own orders
            return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return Order.objects.filter(seller=self.request.user.seller_profile)
        else:
            return Order.objects.filter(user=self.request.user)

class ReturnRequestListView(generics.ListAPIView):
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'refund_type']
    ordering_fields = ['created_at', 'refund_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return ReturnRequest.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return ReturnRequest.objects.filter(user=self.request.user)

class ReturnRequestDetailView(generics.RetrieveAPIView):
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return ReturnRequest.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return ReturnRequest.objects.filter(user=self.request.user)

class ReturnRequestUpdateView(generics.UpdateAPIView):
    serializer_class = ReturnRequestUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return ReturnRequest.objects.all()

# Convert to APIView for custom operations
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's active cart with custom logic"""
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            
            # Calculate totals
            total_items = cart.items.count()
            total_amount = sum(item.total_price for item in cart.items.all())
            
            # Update cart totals
            cart.total_amount = total_amount
            cart.save()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({'message': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        """Add item to cart with custom validation"""
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check product availability
                product = serializer.validated_data.get('product')
                quantity = serializer.validated_data.get('quantity', 1)
                
                if product.stock_quantity < quantity:
                    return Response({
                        'error': f'Only {product.stock_quantity} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not product.is_active or product.status != 'approved':
                    return Response({
                        'error': 'Product is not available for purchase'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_item = serializer.save()
                
                return Response({
                    'message': 'Item added to cart successfully',
                    'cart_item': CartItemSerializer(cart_item).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error adding item to cart: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, item_id):
        """Get cart item and check ownership"""
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=self.request.user,
                cart__is_active=True
            )
            return cart_item
        except CartItem.DoesNotExist:
            return None
    
    def put(self, request, item_id):
        """Update cart item quantity with custom validation"""
        cart_item = self.get_object(item_id)
        if not cart_item:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                new_quantity = serializer.validated_data.get('quantity')
                
                # Check stock availability
                if cart_item.product.stock_quantity < new_quantity:
                    return Response({
                        'error': f'Only {cart_item.product.stock_quantity} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                
                return Response({
                    'message': 'Cart item updated successfully',
                    'cart_item': CartItemSerializer(cart_item).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating cart item: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, item_id):
        """Remove item from cart with custom logic"""
        cart_item = self.get_object(item_id)
        if not cart_item:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            cart_item.delete()
            
            # Update cart totals
            cart = cart_item.cart
            cart.total_amount = sum(item.total_price for item in cart.items.all())
            cart.save()
            
            return Response({'message': 'Item removed from cart successfully'})
            
        except Exception as e:
            return Response({
                'error': f'Error removing item from cart: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Clear all items from cart with custom logic"""
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            
            # Check if cart has items
            if not cart.items.exists():
                return Response({'message': 'Cart is already empty'}, status=status.HTTP_200_OK)
            
            # Clear items
            cart.items.all().delete()
            cart.total_amount = 0
            cart.save()
            
            return Response({'message': 'Cart cleared successfully'})
            
        except Cart.DoesNotExist:
            return Response({'message': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error clearing cart: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create orders with custom validation and processing"""
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                cart_id = serializer.validated_data['cart_id']
                cart = Cart.objects.get(id=cart_id, user=request.user, is_active=True)
                
                # Validate cart
                if not cart.items.exists():
                    return Response({
                        'error': 'Cannot create order from empty cart'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check stock availability
                for item in cart.items.all():
                    if item.product.stock_quantity < item.quantity:
                        return Response({
                            'error': f'Insufficient stock for {item.product.name}. Available: {item.product.stock_quantity}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create orders
                orders = serializer.save()
                
                if isinstance(orders, list):
                    # Multiple orders created (multi-vendor)
                    order_data = [OrderSerializer(order).data for order in orders]
                    return Response({
                        'message': f'{len(orders)} orders created successfully',
                        'orders': order_data
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Single order created
                    return Response({
                        'message': 'Order created successfully',
                        'order': OrderSerializer(orders).data
                    }, status=status.HTTP_201_CREATED)
                
            except Cart.DoesNotExist:
                return Response({
                    'error': 'Invalid cart'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': f'Error creating order: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get order and check access"""
        try:
            if hasattr(self.request.user, 'seller_profile'):
                return Order.objects.get(id=pk, seller=self.request.user.seller_profile)
            else:
                return Order.objects.get(id=pk, user=self.request.user)
        except Order.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update order with custom validation"""
        order = self.get_object(pk)
        if not order:
            return Response({'error': 'Order not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Validate status transitions
                new_status = serializer.validated_data.get('status')
                if new_status and not self._is_valid_status_transition(order.status, new_status):
                    return Response({
                        'error': f'Invalid status transition from {order.status} to {new_status}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create status update
                OrderStatus.objects.create(
                    order=order,
                    status=new_status or order.status,
                    notes=serializer.validated_data.get('notes', 'Order updated'),
                    updated_by=request.user
                )
                
                serializer.save()
                
                return Response({
                    'message': 'Order updated successfully',
                    'order': OrderSerializer(order).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating order: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _is_valid_status_transition(self, current_status, new_status):
        """Validate order status transitions"""
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'returned'],
            'delivered': ['returned'],
            'cancelled': [],
            'returned': []
        }
        return new_status in valid_transitions.get(current_status, [])

class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_id):
        """Cancel an order with custom validation"""
        try:
            if hasattr(request.user, 'seller_profile'):
                order = Order.objects.get(
                    id=order_id,
                    seller=request.user.seller_profile
                )
            else:
                order = Order.objects.get(
                    id=order_id,
                    user=request.user
                )
            
            # Check if order can be cancelled
            if order.status not in ['pending', 'confirmed']:
                return Response({
                    'error': 'Order cannot be cancelled at this stage'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if payment was made
            if order.payment_status == 'paid':
                return Response({
                    'error': 'Cannot cancel order with completed payment. Please contact support for refund.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                order.status = 'cancelled'
                order.save()
                
                # Create status update
                OrderStatus.objects.create(
                    order=order,
                    status='cancelled',
                    notes='Order cancelled by user',
                    updated_by=request.user
                )
                
                # Restore stock
                for item in order.items.all():
                    item.product.stock_quantity += item.quantity
                    item.product.save()
                
                return Response({'message': 'Order cancelled successfully'})
                
            except Exception as e:
                return Response({
                    'error': f'Error cancelling order: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class ReturnRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create return request with custom validation"""
        serializer = ReturnRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Validate return eligibility
                order = serializer.validated_data.get('order')
                
                if order.status != 'delivered':
                    return Response({
                        'error': 'Only delivered orders can be returned'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if order.user != request.user:
                    return Response({
                        'error': 'You can only return your own orders'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Check return window (e.g., 30 days)
                from django.utils import timezone
                from datetime import timedelta
                
                if order.delivered_at and (timezone.now() - order.delivered_at) > timedelta(days=30):
                    return Response({
                        'error': 'Return window has expired (30 days from delivery)'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if return already exists
                if ReturnRequest.objects.filter(order=order).exists():
                    return Response({
                        'error': 'Return request already exists for this order'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return_request = serializer.save()
                
                return Response({
                    'message': 'Return request created successfully',
                    'return_request': ReturnRequestSerializer(return_request).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating return request: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, order_id):
        """Get order tracking information with custom logic"""
        try:
            if hasattr(request.user, 'seller_profile'):
                order = Order.objects.get(
                    id=order_id,
                    seller=request.user.seller_profile
                )
            else:
                order = Order.objects.get(
                    id=order_id,
                    user=request.user
                )
            
            status_history = OrderStatus.objects.filter(order=order).order_by('created_at')
            
            # Calculate estimated delivery
            estimated_delivery = None
            if order.status in ['shipped', 'processing']:
                from django.utils import timezone
                from datetime import timedelta
                estimated_delivery = timezone.now() + timedelta(days=3)  # Example: 3 days
            
            return Response({
                'order_number': order.order_number,
                'current_status': order.status,
                'tracking_number': order.tracking_number,
                'estimated_delivery': estimated_delivery,
                'status_history': [
                    {
                        'status': status.status,
                        'notes': status.notes,
                        'timestamp': status.created_at,
                        'updated_by': status.updated_by.name if status.updated_by else None
                    }
                    for status in status_history
                ]
            })
            
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error retrieving tracking info: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Custom API endpoints
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    """Process checkout and create orders with custom logic"""
    serializer = CartCheckoutSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            # Validate checkout data
            cart_id = serializer.validated_data['cart_id']
            cart = Cart.objects.get(id=cart_id, user=request.user, is_active=True)
            
            if not cart.items.exists():
                return Response({
                    'error': 'Cannot checkout empty cart'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check stock availability
            for item in cart.items.all():
                if item.product.stock_quantity < item.quantity:
                    return Response({
                        'error': f'Insufficient stock for {item.product.name}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create orders
            order_serializer = OrderCreateSerializer(data=serializer.validated_data, context={'request': request})
            if order_serializer.is_valid():
                orders = order_serializer.save()
                
                if isinstance(orders, list):
                    return Response({
                        'message': f'{len(orders)} orders created successfully',
                        'orders': [OrderSerializer(order).data for order in orders]
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'message': 'Order created successfully',
                        'order': OrderSerializer(orders).data
                    }, status=status.HTTP_201_CREATED)
            
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Cart.DoesNotExist:
            return Response({
                'error': 'Invalid cart'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Checkout error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def order_statistics(request):
    """Get order statistics for dashboard with custom calculations"""
    try:
        if hasattr(request.user, 'seller_profile'):
            # Seller statistics
            total_orders = Order.objects.filter(seller=request.user.seller_profile).count()
            pending_orders = Order.objects.filter(seller=request.user.seller_profile, status='pending').count()
            completed_orders = Order.objects.filter(seller=request.user.seller_profile, status='delivered').count()
            total_revenue = Order.objects.filter(
                seller=request.user.seller_profile,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Calculate average order value
            avg_order_value = 0
            if total_orders > 0:
                avg_order_value = total_revenue / total_orders
            
            return Response({
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'total_revenue': total_revenue,
                'average_order_value': round(avg_order_value, 2)
            })
        else:
            # Customer statistics
            total_orders = Order.objects.filter(user=request.user).count()
            active_orders = Order.objects.filter(
                user=request.user,
                status__in=['pending', 'confirmed', 'processing', 'shipped']
            ).count()
            
            # Calculate total spent
            total_spent = Order.objects.filter(
                user=request.user,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            return Response({
                'total_orders': total_orders,
                'active_orders': active_orders,
                'total_spent': total_spent
            })
            
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
