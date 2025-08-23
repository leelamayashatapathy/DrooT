from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from .models import PaymentMethod, Payment, Refund, PayoutRequest, Commission
from .serializers import (
    PaymentMethodSerializer, PaymentSerializer, PaymentCreateSerializer,
    PaymentUpdateSerializer, RefundSerializer, RefundCreateSerializer,
    RefundUpdateSerializer, PayoutRequestSerializer, PayoutRequestCreateSerializer,
    PayoutRequestUpdateSerializer, CommissionSerializer, PaymentProcessSerializer,
    PaymentWebhookSerializer
)

# Keep generics for simple listing and retrieval
class PaymentMethodListView(generics.ListAPIView):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

class PaymentMethodDetailView(generics.RetrieveAPIView):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'order']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            # Seller view - show payments for their orders
            return Payment.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            # Customer view - show their own payments
            return Payment.objects.filter(user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return Payment.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return Payment.objects.filter(user=self.request.user)

class RefundListView(generics.ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'refund_type']
    ordering_fields = ['created_at', 'refund_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return Refund.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return Refund.objects.filter(user=self.request.user)

class RefundDetailView(generics.RetrieveAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return Refund.objects.filter(order__seller=self.request.user.seller_profile)
        else:
            return Refund.objects.filter(user=self.request.user)

class RefundUpdateView(generics.UpdateAPIView):
    serializer_class = RefundUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Refund.objects.all()

class PayoutRequestListView(generics.ListAPIView):
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'requested_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return PayoutRequest.objects.filter(seller=self.request.user.seller_profile)
        else:
            return PayoutRequest.objects.none()  # Customers can't see payout requests

class PayoutRequestDetailView(generics.RetrieveAPIView):
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'seller_profile'):
            return PayoutRequest.objects.filter(seller=self.request.user.seller_profile)
        else:
            return PayoutRequest.objects.none()

class PayoutRequestUpdateView(generics.UpdateAPIView):
    serializer_class = PayoutRequestUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return PayoutRequest.objects.all()

class CommissionListView(generics.ListAPIView):
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['seller', 'category', 'is_active']

class CommissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAdminUser]

class CommissionCreateView(generics.CreateAPIView):
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAdminUser]

# Convert to APIView for custom operations
class PaymentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create payment with custom validation"""
        serializer = PaymentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Validate order ownership
                order = serializer.validated_data.get('order')
                if order.user != request.user:
                    return Response({
                        'error': 'You can only create payments for your own orders'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Check if payment already exists
                if Payment.objects.filter(order=order).exists():
                    return Response({
                        'error': 'Payment already exists for this order'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Calculate processing fee based on payment method
                payment_method = serializer.validated_data.get('payment_method')
                amount = serializer.validated_data.get('amount')
                processing_fee = self._calculate_processing_fee(payment_method, amount)
                
                # Create payment
                payment = serializer.save()
                payment.processing_fee = processing_fee
                payment.save()
                
                return Response({
                    'message': 'Payment created successfully',
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating payment: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_processing_fee(self, payment_method, amount):
        """Calculate processing fee based on payment method"""
        if payment_method.name.lower() == 'credit_card':
            return amount * 0.029 + 0.30  # 2.9% + $0.30
        elif payment_method.name.lower() == 'debit_card':
            return amount * 0.025 + 0.25  # 2.5% + $0.25
        elif payment_method.name.lower() == 'bank_transfer':
            return amount * 0.01  # 1%
        else:
            return 0.00

class PaymentUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get payment and check access"""
        try:
            if hasattr(self.request.user, 'seller_profile'):
                return Payment.objects.get(id=pk, order__seller=self.request.user.seller_profile)
            else:
                return Payment.objects.get(id=pk, user=self.request.user)
        except Payment.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update payment with custom validation"""
        payment = self.get_object(pk)
        if not payment:
            return Response({'error': 'Payment not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentUpdateSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Validate status transitions
                new_status = serializer.validated_data.get('status')
                if new_status and not self._is_valid_status_transition(payment.status, new_status):
                    return Response({
                        'error': f'Invalid status transition from {payment.status} to {new_status}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update payment
                serializer.save()
                
                # Update order payment status if payment completed
                if new_status == 'completed':
                    payment.order.payment_status = 'paid'
                    payment.order.save()
                
                return Response({
                    'message': 'Payment updated successfully',
                    'payment': PaymentSerializer(payment).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating payment: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _is_valid_status_transition(self, current_status, new_status):
        """Validate payment status transitions"""
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'failed', 'cancelled'],
            'completed': [],
            'failed': ['processing'],
            'cancelled': []
        }
        return new_status in valid_transitions.get(current_status, [])

class RefundCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create refund with custom validation"""
        serializer = RefundCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                payment = serializer.validated_data.get('payment')
                refund_amount = serializer.validated_data.get('refund_amount')
                
                # Validate payment ownership
                if payment.user != request.user:
                    return Response({
                        'error': 'You can only create refunds for your own payments'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Check if payment is completed
                if payment.status != 'completed':
                    return Response({
                        'error': 'Only completed payments can be refunded'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check refund amount
                if refund_amount > payment.amount:
                    return Response({
                        'error': 'Refund amount cannot exceed payment amount'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if refund already exists
                if Refund.objects.filter(payment=payment).exists():
                    return Response({
                        'error': 'Refund already exists for this payment'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create refund
                refund = serializer.save()
                
                return Response({
                    'message': 'Refund request created successfully',
                    'refund': RefundSerializer(refund).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating refund: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PayoutRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create payout request with custom validation"""
        serializer = PayoutRequestCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check if user is a seller
                if not hasattr(request.user, 'seller_profile'):
                    return Response({
                        'error': 'Only sellers can request payouts'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                requested_amount = serializer.validated_data.get('requested_amount')
                
                # Check available balance
                available_balance = self._calculate_available_balance(request.user.seller_profile)
                if requested_amount > available_balance:
                    return Response({
                        'error': f'Insufficient balance. Available: ${available_balance}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check minimum payout amount
                if requested_amount < 50.00:  # $50 minimum
                    return Response({
                        'error': 'Minimum payout amount is $50.00'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if there's already a pending payout
                if PayoutRequest.objects.filter(
                    seller=request.user.seller_profile,
                    status='pending'
                ).exists():
                    return Response({
                        'error': 'You already have a pending payout request'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create payout request
                payout_request = serializer.save()
                
                return Response({
                    'message': 'Payout request created successfully',
                    'payout_request': PayoutRequestSerializer(payout_request).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating payout request: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _calculate_available_balance(self, seller_profile):
        """Calculate available balance for seller"""
        total_revenue = Payment.objects.filter(
            order__seller=seller_profile,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_payouts = PayoutRequest.objects.filter(
            seller=seller_profile,
            status='approved'
        ).aggregate(total=Sum('requested_amount'))['total'] or 0
        
        return total_revenue - total_payouts

# Custom API endpoints
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request):
    """Process a payment for an order with custom logic"""
    serializer = PaymentProcessSerializer(data=request.data)
    if serializer.is_valid():
        try:
            order_id = serializer.validated_data['order_id']
            payment_method_id = serializer.validated_data['payment_method_id']
            amount = serializer.validated_data['amount']
            
            # Get order and payment method
            try:
                from Orders.models import Order
                order = Order.objects.get(id=order_id, user=request.user)
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
            except (Order.DoesNotExist, PaymentMethod.DoesNotExist):
                return Response({'error': 'Invalid order or payment method'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate order amount
            if amount != order.total_amount:
                return Response({
                    'error': f'Payment amount must match order total: ${order.total_amount}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if payment already exists
            if Payment.objects.filter(order=order).exists():
                return Response({
                    'error': 'Payment already exists for this order'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                payment_method=payment_method,
                amount=amount,
                status='processing'
            )
            
            # In a real application, integrate with payment gateway here
            # For now, simulate successful payment
            payment.status = 'completed'
            payment.transaction_id = f"TXN-{payment.payment_id}"
            payment.processed_at = timezone.now()
            payment.save()
            
            # Update order payment status
            order.payment_status = 'paid'
            order.save()
            
            return Response({
                'message': 'Payment processed successfully',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Payment processing error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def payment_webhook(request):
    """Handle payment gateway webhooks with custom logic"""
    serializer = PaymentWebhookSerializer(data=request.data)
    if serializer.is_valid():
        try:
            payment_id = serializer.validated_data['payment_id']
            status = serializer.validated_data['status']
            
            try:
                payment = Payment.objects.get(payment_id=payment_id)
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Update payment status
            payment.status = status
            
            if status == 'completed':
                payment.transaction_id = serializer.validated_data.get('transaction_id', '')
                payment.processed_at = timezone.now()
                # Update order payment status
                payment.order.payment_status = 'paid'
                payment.order.save()
            elif status == 'failed':
                payment.failed_at = timezone.now()
                payment.failure_reason = 'Payment gateway failure'
            elif status == 'cancelled':
                payment.cancelled_at = timezone.now()
            
            payment.save()
            
            return Response({'message': 'Webhook processed successfully'})
            
        except Exception as e:
            return Response({
                'error': f'Webhook processing error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_statistics(request):
    """Get payment statistics for dashboard with custom calculations"""
    try:
        if hasattr(request.user, 'seller_profile'):
            # Seller statistics
            total_payments = Payment.objects.filter(
                order__seller=request.user.seller_profile,
                status='completed'
            ).count()
            
            total_revenue = Payment.objects.filter(
                order__seller=request.user.seller_profile,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            pending_payouts = PayoutRequest.objects.filter(
                seller=request.user.seller_profile,
                status='pending'
            ).aggregate(total=Sum('requested_amount'))['total'] or 0
            
            # Calculate processing fees
            total_fees = Payment.objects.filter(
                order__seller=request.user.seller_profile,
                status='completed'
            ).aggregate(total=Sum('processing_fee'))['total'] or 0
            
            return Response({
                'total_payments': total_payments,
                'total_revenue': total_revenue,
                'pending_payouts': pending_payouts,
                'total_processing_fees': total_fees,
                'net_revenue': total_revenue - total_fees
            })
        else:
            # Customer statistics
            total_payments = Payment.objects.filter(
                user=request.user,
                status='completed'
            ).count()
            
            total_spent = Payment.objects.filter(
                user=request.user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate average payment amount
            avg_payment = 0
            if total_payments > 0:
                avg_payment = total_spent / total_payments
            
            return Response({
                'total_payments': total_payments,
                'total_spent': total_spent,
                'average_payment': round(avg_payment, 2)
            })
            
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_refund(request, payment_id):
    """Request a refund for a payment with custom validation"""
    try:
        payment = Payment.objects.get(
            payment_id=payment_id,
            user=request.user,
            status='completed'
        )
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if refund already exists
    if Refund.objects.filter(payment=payment).exists():
        return Response({'error': 'Refund already requested'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check refund eligibility (e.g., within 30 days)
    from datetime import timedelta
    if payment.processed_at and (timezone.now() - payment.processed_at) > timedelta(days=30):
        return Response({
            'error': 'Refund window has expired (30 days from payment)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create refund request
        refund = Refund.objects.create(
            payment=payment,
            user=request.user,
            order=payment.order,
            refund_amount=payment.amount,
            refund_type='full',
            reason='Customer requested refund'
        )
        
        return Response({
            'message': 'Refund request created successfully',
            'refund': RefundSerializer(refund).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error creating refund request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
