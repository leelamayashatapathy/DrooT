from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from Users.models import SellerProfile
from Users.serializers import SellerProfileSerializer, SellerProfileCreateSerializer,UserRegistrationSerializer
from .serializers import SellerDashboardSerializer, SellerAnalyticsSerializer
from Products.models import Product
from Orders.models import Order

class SellerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user_data = request.data.get("user")
        print(user_data)
        seller_data = request.data.get("seller_profile")
        # Check if user already has a seller profile
        if hasattr(request.user, 'seller_profile'):
            return Response(
                {'error': 'User already has a seller profile'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_serializer = UserRegistrationSerializer(data=user_data)
        print(user_serializer)
        if not user_serializer.is_valid():
            print(user_serializer.errors)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = user_serializer.save()
        user.is_seller = True
        user.save()
        print(user)
        # Step 2: Create Seller Profile
        seller_serializer = SellerProfileCreateSerializer(
            data=seller_data, context={"request": request, "user": user}
        )
        if not seller_serializer.is_valid():
            user.delete()  # rollback user if seller profile invalid
            return Response(seller_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        seller_profile = seller_serializer.save()

        # Step 3: Create JWT Tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "phone": user.phone,
                    "gender": user.gender,
                    "is_seller": user.is_seller,
                },
                "seller_profile": SellerProfileSerializer(seller_profile).data,
            },
            status=status.HTTP_201_CREATED,
        )

class SellerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            seller_profile = request.user.seller_profile
            serializer = SellerProfileSerializer(seller_profile)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request):
        try:
            seller_profile = request.user.seller_profile
            serializer = SellerProfileCreateSerializer(seller_profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(SellerProfileSerializer(seller_profile).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            seller_profile = request.user.seller_profile
            
            # Get seller statistics
            total_products = Product.objects.filter(seller=seller_profile).count()
            total_orders = Order.objects.filter(items__product__seller=seller_profile).distinct().count()
            pending_orders = Order.objects.filter(
                items__product__seller=seller_profile,
                status__in=['pending', 'processing']
            ).distinct().count()
            
            # Calculate total revenue
            total_revenue = Order.objects.filter(
                items__product__seller=seller_profile,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            dashboard_data = {
                'profile': seller_profile,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'pending_orders': pending_orders
            }
            
            serializer = SellerDashboardSerializer(dashboard_data)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            seller_profile = request.user.seller_profile
            products = Product.objects.filter(seller=seller_profile)
            
            # Return basic product data
            product_data = []
            for product in products:
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'base_price': product.base_price,
                    'sale_price': product.sale_price,
                    'stock_quantity': product.stock_quantity,
                    'status': product.status,
                    'is_active': product.is_active
                })
            
            return Response({
                'count': len(product_data),
                'results': product_data
            })
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerProductCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            seller_profile = request.user.seller_profile
            
            # Add seller to product data
            product_data = request.data.copy()
            product_data['seller'] = seller_profile.id
            
            # Create product (you'll need to implement Product creation logic)
            # For now, return a placeholder response
            return Response(
                {'message': 'Product creation endpoint - implement with Product model'},
                status=status.HTTP_201_CREATED
            )
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            seller_profile = request.user.seller_profile
            product = get_object_or_404(Product, pk=pk, seller=seller_profile)
            
            # Return product data (implement with Product serializer)
            return Response({'message': f'Product {pk} details'})
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerProductUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        try:
            seller_profile = request.user.seller_profile
            product = get_object_or_404(Product, pk=pk, seller=seller_profile)
            
            # Update product logic here
            return Response({'message': f'Product {pk} updated'})
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerProductDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            seller_profile = request.user.seller_profile
            product = get_object_or_404(Product, pk=pk, seller=seller_profile)
            
            # Delete product logic here
            return Response({'message': f'Product {pk} deleted'})
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            seller_profile = request.user.seller_profile
            orders = Order.objects.filter(items__product__seller=seller_profile).distinct()
            
            # Return basic order data
            order_data = []
            for order in orders:
                order_data.append({
                    'id': order.id,
                    'order_number': order.order_number,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'subtotal': order.subtotal,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at
                })
            
            return Response({
                'count': len(order_data),
                'results': order_data
            })
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerOrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            seller_profile = request.user.seller_profile
            order = get_object_or_404(
                Order, 
                pk=pk, 
                items__product__seller=seller_profile
            )
            
            # Return order data (implement with Order serializer)
            return Response({'message': f'Order {pk} details'})
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SellerAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            seller_profile = request.user.seller_profile
            
            # Get analytics data with safe defaults
            total_products = Product.objects.filter(seller=seller_profile).count()
            total_orders = Order.objects.filter(items__product__seller=seller_profile).distinct().count()
            total_revenue = Order.objects.filter(
                items__product__seller=seller_profile,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Monthly revenue (last 6 months) - handle empty data
            monthly_revenue = []
            for i in range(6):
                month_start = timezone.now() - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                month_revenue = Order.objects.filter(
                    items__product__seller=seller_profile,
                    status='completed',
                    created_at__range=[month_start, month_end]
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                monthly_revenue.append({
                    'month': month_start.strftime('%B %Y'),
                    'revenue': month_revenue
                })
            
            # Top products by sales - handle empty data safely
            try:
                top_products = Product.objects.filter(seller=seller_profile).annotate(
                    sales_count=Count('order_items')
                ).order_by('-sales_count')[:5]
                top_products_data = [{'id': p.id, 'name': p.name, 'sales': p.sales_count} for p in top_products]
            except:
                top_products_data = []
            
            # Order status distribution - handle empty data safely
            try:
                order_status_distribution = Order.objects.filter(
                    items__product__seller=seller_profile
                ).values('status').annotate(count=Count('id'))
                status_distribution = {item['status']: item['count'] for item in order_status_distribution}
            except:
                status_distribution = {}
            
            analytics_data = {
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'top_products': top_products_data,
                'order_status_distribution': status_distribution
            }
            
            serializer = SellerAnalyticsSerializer(analytics_data)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Return safe default data if there are any errors
            return Response({
                'total_products': 0,
                'total_orders': 0,
                'total_revenue': 0,
                'monthly_revenue': [],
                'top_products': [],
                'order_status_distribution': {}
            })
