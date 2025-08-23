from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Coupon, CouponUsage, Discount, Promotion, Campaign, ReferralProgram, Referral
from .serializers import (
    CouponSerializer, CouponCreateSerializer, CouponUpdateSerializer,
    CouponUsageSerializer, DiscountSerializer, DiscountCreateSerializer,
    PromotionSerializer, PromotionCreateSerializer, CampaignSerializer,
    CampaignCreateSerializer, ReferralProgramSerializer, ReferralProgramCreateSerializer,
    ReferralSerializer, ReferralCreateSerializer, CouponValidationSerializer,
    PromotionSearchSerializer
)

# Keep generics for simple listing and retrieval
class CouponListView(generics.ListAPIView):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

class CouponDetailView(generics.RetrieveAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

class CouponUsageListView(generics.ListAPIView):
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['coupon', 'user', 'order']
    ordering_fields = ['used_at', 'created_at']
    ordering = ['-used_at']

class CouponUsageDetailView(generics.RetrieveAPIView):
    queryset = CouponUsage.objects.all()
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAdminUser]

class DiscountListView(generics.ListAPIView):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]

class DiscountDetailView(generics.RetrieveAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]

class PromotionListView(generics.ListAPIView):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAdminUser]

class PromotionDetailView(generics.RetrieveAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAdminUser]

class CampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.filter(status='active')
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAdminUser]

class CampaignDetailView(generics.RetrieveAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAdminUser]

class ReferralProgramListView(generics.ListAPIView):
    queryset = ReferralProgram.objects.filter(is_active=True)
    serializer_class = ReferralProgramSerializer
    permission_classes = [permissions.IsAdminUser]

class ReferralProgramDetailView(generics.RetrieveAPIView):
    queryset = ReferralProgram.objects.all()
    serializer_class = ReferralProgramSerializer
    permission_classes = [permissions.IsAdminUser]

class ReferralListView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['referrer', 'referee', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

class ReferralDetailView(generics.RetrieveAPIView):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAdminUser]

# Convert to APIView for custom operations
class CouponCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create coupon with custom validation"""
        serializer = CouponCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                coupon = serializer.save()
                
                return Response({
                    'message': 'Coupon created successfully',
                    'coupon': CouponSerializer(coupon).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating coupon: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get coupon and check access"""
        try:
            return Coupon.objects.get(id=pk)
        except Coupon.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update coupon with custom logic"""
        coupon = self.get_object(pk)
        if not coupon:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CouponUpdateSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                return Response({
                    'message': 'Coupon updated successfully',
                    'coupon': CouponSerializer(coupon).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating coupon: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscountCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create discount with custom validation"""
        serializer = DiscountCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                discount = serializer.save()
                
                return Response({
                    'message': 'Discount created successfully',
                    'discount': DiscountSerializer(discount).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating discount: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscountUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get discount and check access"""
        try:
            return Discount.objects.get(id=pk)
        except Discount.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update discount with custom logic"""
        discount = self.get_object(pk)
        if not discount:
            return Response({'error': 'Discount not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DiscountCreateSerializer(discount, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                return Response({
                    'message': 'Discount updated successfully',
                    'discount': DiscountSerializer(discount).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating discount: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromotionCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create promotion with custom validation"""
        serializer = PromotionCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                promotion = serializer.save()
                
                return Response({
                    'message': 'Promotion created successfully',
                    'promotion': PromotionSerializer(promotion).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating promotion: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromotionUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get promotion and check access"""
        try:
            return Promotion.objects.get(id=pk)
        except Promotion.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update promotion with custom logic"""
        promotion = self.get_object(pk)
        if not promotion:
            return Response({'error': 'Promotion not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PromotionCreateSerializer(promotion, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                return Response({
                    'message': 'Promotion updated successfully',
                    'promotion': PromotionSerializer(promotion).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating promotion: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CampaignCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create campaign with custom validation"""
        serializer = CampaignCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                campaign = serializer.save()
                
                return Response({
                    'message': 'Campaign created successfully',
                    'campaign': CampaignSerializer(campaign).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating campaign: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CampaignUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get campaign and check access"""
        try:
            return Campaign.objects.get(id=pk)
        except Campaign.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update campaign with custom logic"""
        campaign = self.get_object(pk)
        if not campaign:
            return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CampaignCreateSerializer(campaign, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                return Response({
                    'message': 'Campaign updated successfully',
                    'campaign': CampaignSerializer(campaign).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating campaign: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReferralProgramCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create referral program with custom validation"""
        serializer = ReferralProgramCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                referral_program = serializer.save()
                
                return Response({
                    'message': 'Referral program created successfully',
                    'referral_program': ReferralProgramSerializer(referral_program).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating referral program: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReferralProgramUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get referral program and check access"""
        try:
            return ReferralProgram.objects.get(id=pk)
        except ReferralProgram.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update referral program with custom logic"""
        referral_program = self.get_object(pk)
        if not referral_program:
            return Response({'error': 'Referral program not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReferralProgramCreateSerializer(referral_program, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                return Response({
                    'message': 'Referral program updated successfully',
                    'referral_program': ReferralProgramSerializer(referral_program).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating referral program: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReferralCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create referral with custom validation"""
        serializer = ReferralCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                referee_email = serializer.validated_data['referee_email']
                
                # Create referral
                referral = Referral.objects.create(
                    referrer=request.user,
                    referee_email=referee_email,
                    status='pending'
                )
                
                return Response({
                    'message': 'Referral created successfully',
                    'referral': ReferralSerializer(referral).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating referral: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromotionSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Search promotions with custom logic"""
        serializer = PromotionSearchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                query = serializer.validated_data.get('query', '')
                promotion_type = serializer.validated_data.get('promotion_type')
                is_active = serializer.validated_data.get('is_active')
                date_from = serializer.validated_data.get('date_from')
                date_to = serializer.validated_data.get('date_to')
                page = serializer.validated_data.get('page', 1)
                page_size = serializer.validated_data.get('page_size', 20)
                
                queryset = Promotion.objects.all()
                
                # Apply filters
                if query:
                    queryset = queryset.filter(
                        Q(name__icontains=query) |
                        Q(description__icontains=query)
                    )
                
                if promotion_type:
                    queryset = queryset.filter(promotion_type=promotion_type)
                
                if is_active is not None:
                    queryset = queryset.filter(is_active=is_active)
                
                if date_from:
                    queryset = queryset.filter(valid_from__date__gte=date_from)
                
                if date_to:
                    queryset = queryset.filter(valid_until__date__lte=date_to)
                
                # Order by creation date
                queryset = queryset.order_by('-created_at')
                
                # Pagination
                total_count = queryset.count()
                start = (page - 1) * page_size
                end = start + page_size
                
                promotions = queryset[start:end]
                
                serializer_data = PromotionSerializer(promotions, many=True).data
                
                return Response({
                    'promotions': serializer_data,
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                })
                
            except Exception as e:
                return Response({
                    'error': f'Search error: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom API endpoints
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_coupon(request):
    """Validate coupon code"""
    serializer = CouponValidationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            coupon = serializer.validated_data['code']
            order_amount = serializer.validated_data['order_amount']
            
            # Calculate discount amount
            if coupon.discount_type == 'percentage':
                discount_amount = order_amount * (coupon.discount_value / 100)
            else:
                discount_amount = coupon.discount_value
            
            return Response({
                'valid': True,
                'coupon': CouponSerializer(coupon).data,
                'discount_amount': discount_amount,
                'final_amount': order_amount - discount_amount
            })
            
        except Exception as e:
            return Response({
                'error': f'Coupon validation error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def promotion_statistics(request):
    """Get promotion statistics for admin dashboard"""
    try:
        total_coupons = Coupon.objects.count()
        active_coupons = Coupon.objects.filter(is_active=True).count()
        total_promotions = Promotion.objects.count()
        active_promotions = Promotion.objects.filter(is_active=True).count()
        
        # Coupon usage statistics
        total_coupon_usage = CouponUsage.objects.count()
        recent_coupon_usage = CouponUsage.objects.filter(
            used_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Referral statistics
        total_referrals = Referral.objects.count()
        successful_referrals = Referral.objects.filter(status='completed').count()
        
        return Response({
            'coupons': {
                'total': total_coupons,
                'active': active_coupons,
                'usage': total_coupon_usage,
                'recent_usage': recent_coupon_usage
            },
            'promotions': {
                'total': total_promotions,
                'active': active_promotions
            },
            'referrals': {
                'total': total_referrals,
                'successful': successful_referrals,
                'success_rate': (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
