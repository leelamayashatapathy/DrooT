from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductReview
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, ProductCreateSerializer,
    ProductUpdateSerializer, ProductListSerializer, ProductDetailSerializer,
    CategoryProductSerializer, ProductSearchSerializer, ProductImageSerializer,
    ProductVariantSerializer, ProductReviewSerializer
)

# Keep generics for simple listing and retrieval
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryProductSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    
    
class CreateBrand(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]

class BrandDetailView(generics.RetrieveAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'condition', 'is_featured']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['price', 'created_at', 'average_rating', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, status='approved')
        
        # Price filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Rating filtering
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(average_rating__gte=rating)
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True, status='approved')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Convert to APIView for custom operations
class ProductCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a new product with custom validation and processing"""
        serializer = ProductCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check if user is a seller
                if not hasattr(request.user, 'seller_profile'):
                    return Response({
                        'error': 'Only sellers can create products. Please complete your seller profile first.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Create product
                product = serializer.save()
                
                # Set initial status
                product.status = 'pending'  # Requires admin approval
                product.save()
                
                return Response({
                    'message': 'Product created successfully and pending approval',
                    'product': ProductSerializer(product).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating product: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get product and check ownership"""
        try:
            product = Product.objects.get(id=pk, seller__user=self.request.user)
            return product
        except Product.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update product with custom validation"""
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # If significant changes made, reset to pending status
                if self._has_significant_changes(product, serializer.validated_data):
                    serializer.validated_data['status'] = 'pending'
                
                serializer.save()
                
                return Response({
                    'message': 'Product updated successfully',
                    'product': ProductSerializer(product).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating product: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _has_significant_changes(self, product, validated_data):
        """Check if significant changes were made that require re-approval"""
        significant_fields = ['name', 'description', 'category', 'brand', 'base_price', 'condition']
        for field in significant_fields:
            if field in validated_data and getattr(product, field) != validated_data[field]:
                return True
        return False

class ProductDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get product and check ownership"""
        try:
            product = Product.objects.get(id=pk, seller__user=self.request.user)
            return product
        except Product.DoesNotExist:
            return None
    
    def delete(self, request, pk):
        """Soft delete product with custom logic"""
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Check if product has active orders
            if product.order_items.filter(order__status__in=['pending', 'confirmed', 'processing', 'shipped']).exists():
                return Response({
                    'error': 'Cannot delete product with active orders. Please contact support.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Soft delete
            product.is_active = False
            product.status = 'deleted'
            product.save()
            
            return Response({'message': 'Product deleted successfully'})
            
        except Exception as e:
            return Response({
                'error': f'Error deleting product: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SellerProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active', 'is_featured']
    ordering_fields = ['created_at', 'name', 'base_price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)

class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Advanced product search with custom logic"""
        serializer = ProductSearchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                query = serializer.validated_data.get('query', '')
                category = serializer.validated_data.get('category')
                brand = serializer.validated_data.get('brand')
                min_price = serializer.validated_data.get('min_price')
                max_price = serializer.validated_data.get('max_price')
                condition = serializer.validated_data.get('condition')
                rating = serializer.validated_data.get('rating')
                sort_by = serializer.validated_data.get('sort_by', 'newest')
                
                queryset = Product.objects.filter(is_active=True, status='approved')
                
                # Text search with relevance scoring
                if query:
                    queryset = queryset.filter(
                        Q(name__icontains=query) |
                        Q(description__icontains=query) |
                        Q(tags__icontains=query)
                    )
                    # Boost exact matches
                    queryset = queryset.extra(
                        select={'relevance': 
                            "CASE WHEN name ILIKE %s THEN 3 " +
                            "WHEN name ILIKE %s THEN 2 " +
                            "WHEN description ILIKE %s THEN 1 " +
                            "ELSE 0 END"
                        },
                        select_params=[f'%{query}%', f'{query}%', f'%{query}%']
                    )
                
                # Advanced filtering
                if category:
                    queryset = queryset.filter(category_id=category)
                if brand:
                    queryset = queryset.filter(brand_id=brand)
                if min_price:
                    queryset = queryset.filter(base_price__gte=min_price)
                if max_price:
                    queryset = queryset.filter(base_price__lte=max_price)
                if condition:
                    queryset = queryset.filter(condition=condition)
                if rating:
                    queryset = queryset.filter(average_rating__gte=rating)
                
                # Smart sorting
                if sort_by == 'price_low':
                    queryset = queryset.order_by('base_price')
                elif sort_by == 'price_high':
                    queryset = queryset.order_by('-base_price')
                elif sort_by == 'rating':
                    queryset = queryset.order_by('-average_rating')
                elif sort_by == 'popularity':
                    queryset = queryset.order_by('-view_count', '-purchase_count')
                elif sort_by == 'relevance' and query:
                    queryset = queryset.order_by('-relevance', '-average_rating')
                else:  # newest
                    queryset = queryset.order_by('-created_at')
                
                # Pagination with custom logic
                page = serializer.validated_data.get('page', 1)
                page_size = serializer.validated_data.get('page_size', 20)
                start = (page - 1) * page_size
                end = start + page_size
                
                total_count = queryset.count()
                products = queryset[start:end]
                
                serializer_data = ProductListSerializer(products, many=True).data
                
                return Response({
                    'products': serializer_data,
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'search_metadata': {
                        'query': query,
                        'filters_applied': {
                            'category': category,
                            'brand': brand,
                            'price_range': f"{min_price or 'Any'} - {max_price or 'Any'}",
                            'condition': condition,
                            'rating': rating
                        }
                    }
                })
                
            except Exception as e:
                return Response({
                    'error': f'Search error: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        """Create product review with custom validation"""
        try:
            product = Product.objects.get(id=product_id, is_active=True, status='approved')
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user has purchased this product
        if not product.order_items.filter(order__user=request.user, order__status='delivered').exists():
            return Response({
                'error': 'You can only review products you have purchased and received'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response({
                'error': 'You have already reviewed this product'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                review = serializer.save()
                
                # Update product rating
                self._update_product_rating(product)
                
                return Response({
                    'message': 'Review submitted successfully',
                    'review': ProductReviewSerializer(review).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating review: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _update_product_rating(self, product):
        """Update product average rating and total reviews"""
        reviews = product.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            product.average_rating = round(avg_rating, 2)
            product.total_reviews = reviews.count()
            product.save()

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating', 'helpful_votes']
    ordering = ['-created_at']
    
    def get_queryset(self):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        return ProductReview.objects.filter(product=product, is_approved=True)

class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        """Upload product images with custom processing"""
        try:
            product = Product.objects.get(id=product_id, seller__user=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(images) > 10:  # Limit to 10 images
            return Response({'error': 'Maximum 10 images allowed per product'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uploaded_images = []
            for i, image in enumerate(images):
                # Validate image size and type
                if image.size > 5 * 1024 * 1024:  # 5MB limit
                    continue
                
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image,
                    order=i,
                    is_primary=(i == 0)
                )
                uploaded_images.append(ProductImageSerializer(product_image).data)
            
            return Response({
                'message': f'{len(uploaded_images)} images uploaded successfully',
                'images': uploaded_images
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error uploading images: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductVariantCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        """Create product variant with custom validation"""
        try:
            product = Product.objects.get(id=product_id, seller__user=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductVariantSerializer(data=request.data)
        if serializer.is_valid():
            try:
                variant = serializer.save(product=product)
                
                return Response({
                    'message': 'Variant created successfully',
                    'variant': ProductVariantSerializer(variant).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating variant: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductVariantListView(generics.ListAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        return ProductVariant.objects.filter(product=product, is_active=True)

# Admin actions with custom logic
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_product_featured(request, product_id):
    """Toggle product featured status with custom validation"""
    if not request.user.is_admin:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if product meets featured criteria
        if not product.is_active or product.status != 'approved':
            return Response({
                'error': 'Only active and approved products can be featured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if product.average_rating < 4.0:
            return Response({
                'error': 'Products with rating below 4.0 cannot be featured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product.is_featured = not product.is_featured
        product.save()
        
        return Response({
            'message': f'Product {"featured" if product.is_featured else "unfeatured"} successfully',
            'is_featured': product.is_featured
        })
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error updating product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_product(request, product_id):
    """Approve product with custom validation"""
    if not request.user.is_admin:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        product = Product.objects.get(id=product_id)
        
        if product.status != 'pending':
            return Response({
                'error': 'Product is not pending approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if product has required fields
        if not product.images.exists():
            return Response({
                'error': 'Product must have at least one image before approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product.status = 'approved'
        product.approved_by = request.user
        product.save()
        
        return Response({'message': 'Product approved successfully'})
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error approving product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_product(request, product_id):
    """Reject product with custom feedback"""
    if not request.user.is_admin:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        product = Product.objects.get(id=product_id)
        rejection_reason = request.data.get('rejection_reason', 'Product rejected by admin')
        
        if product.status != 'pending':
            return Response({
                'error': 'Product is not pending approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product.status = 'rejected'
        product.admin_notes = rejection_reason
        product.save()
        
        return Response({
            'message': 'Product rejected successfully',
            'rejection_reason': rejection_reason
        })
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error rejecting product: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
