from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductReview

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_children(self, obj):
        children = Category.objects.filter(parent=obj, is_active=True)
        return CategorySerializer(children, many=True).data
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, status='approved').count()

class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = '__all__'
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, status='approved').count()

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ['user', 'helpful_votes', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['slug', 'sku', 'view_count', 'purchase_count', 'average_rating', 'total_reviews', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'short_description', 'category', 'brand', 
                 'base_price', 'sale_price', 'cost_price', 'stock_quantity', 
                 'min_stock_alert', 'barcode', 'weight', 'dimensions', 'condition',
                 'meta_title', 'meta_description', 'tags', 'images']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['seller'] = self.context['request'].user.seller_profile
        product = Product.objects.create(**validated_data)
        
        for i, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                order=i,
                is_primary=(i == 0)
            )
        
        return product

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'short_description', 'category', 'brand',
                 'base_price', 'sale_price', 'cost_price', 'stock_quantity',
                 'min_stock_alert', 'barcode', 'weight', 'dimensions', 'condition',
                 'meta_title', 'meta_description', 'tags', 'is_active']

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'short_description', 'category', 'brand',
                 'base_price', 'sale_price', 'current_price', 'discount_percentage',
                 'stock_quantity', 'average_rating', 'total_reviews', 'primary_image',
                 'seller_name', 'is_featured', 'created_at']
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

class ProductDetailSerializer(ProductSerializer):
    related_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'short_description', 'category', 'brand',
                 'base_price', 'sale_price', 'cost_price', 'stock_quantity', 'min_stock_alert',
                 'barcode', 'weight', 'dimensions', 'condition', 'status', 'is_featured',
                 'meta_title', 'meta_description', 'tags', 'view_count', 'purchase_count',
                 'average_rating', 'total_reviews', 'images', 'variants', 'reviews',
                 'seller_name', 'created_at', 'updated_at', 'related_products']
    
    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category,
            is_active=True,
            status='approved'
        ).exclude(id=obj.id)[:6]
        return ProductListSerializer(related, many=True).data

class CategoryProductSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'products']
    
    def get_products(self, obj):
        products = obj.products.filter(is_active=True, status='approved')
        return ProductListSerializer(products, many=True).data

class ProductSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    brand = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    condition = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    sort_by = serializers.ChoiceField(
        choices=['price_low', 'price_high', 'newest', 'rating', 'popularity'],
        required=False
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
