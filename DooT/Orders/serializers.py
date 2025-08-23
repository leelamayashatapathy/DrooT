from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, OrderStatus, ReturnRequest
from Products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        variant_id = validated_data.pop('variant_id', None)
        
        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(
            user=self.context['request'].user,
            is_active=True
        )
        
        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product_id=product_id,
            variant_id=variant_id
        ).first()
        
        if existing_item:
            existing_item.quantity += validated_data.get('quantity', 1)
            existing_item.save()
            return existing_item
        else:
            validated_data['cart'] = cart
            validated_data['product_id'] = product_id
            if variant_id:
                validated_data['variant_id'] = variant_id
            return super().create(validated_data)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'order_number', 'user', 'seller', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.IntegerField(write_only=True)
    shipping_address = serializers.CharField(required=True)
    shipping_city = serializers.CharField(required=True)
    shipping_state = serializers.CharField(required=True)
    shipping_country = serializers.CharField(required=True)
    shipping_zip_code = serializers.CharField(required=True)
    shipping_phone = serializers.CharField(required=True)
    
    class Meta:
        model = Order
        fields = ['cart_id', 'shipping_address', 'shipping_city', 'shipping_state',
                 'shipping_country', 'shipping_zip_code', 'shipping_phone', 'notes']
    
    def create(self, validated_data):
        cart_id = validated_data.pop('cart_id')
        cart = Cart.objects.get(id=cart_id, user=self.context['request'].user, is_active=True)
        
        # Group cart items by seller
        seller_items = cart.seller_groups
        
        orders = []
        for seller, items in seller_items.items():
            # Calculate totals for this seller's items
            subtotal = sum(item.total_price for item in items)
            tax_amount = subtotal * 0.1  # 10% tax (simplified)
            shipping_amount = 5.00  # Fixed shipping (simplified)
            total_amount = subtotal + tax_amount + shipping_amount
            
            # Create order for this seller
            order_data = {
                'user': self.context['request'].user,
                'seller': seller,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'shipping_amount': shipping_amount,
                'total_amount': total_amount,
                **validated_data
            }
            
            order = Order.objects.create(**order_data)
            
            # Create order items
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    product_name=item.product.name,
                    variant_name=str(item.variant) if item.variant else '',
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
            
            # Create initial status
            OrderStatus.objects.create(
                order=order,
                status='pending',
                notes='Order created'
            )
            
            orders.append(order)
        
        # Clear cart
        cart.is_active = False
        cart.save()
        
        return orders[0] if len(orders) == 1 else orders

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'estimated_delivery', 'notes']
        read_only_fields = ['id', 'order_number', 'user', 'seller']

class ReturnRequestSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = ReturnRequest
        fields = '__all__'
        read_only_fields = ['id', 'user', 'order', 'status', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReturnRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = ['status', 'refund_amount', 'admin_notes']
        read_only_fields = ['id', 'user', 'order', 'created_at']

class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

class CartCheckoutSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField()
    shipping_state = serializers.CharField()
    shipping_country = serializers.CharField()
    shipping_zip_code = serializers.CharField()
    shipping_phone = serializers.CharField()
    payment_method = serializers.CharField()
    notes = serializers.CharField(required=False)
    
    def validate_cart_id(self, value):
        user = self.context['request'].user
        try:
            cart = Cart.objects.get(id=value, user=user, is_active=True)
            if not cart.items.exists():
                raise serializers.ValidationError("Cart is empty")
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Invalid cart")
        return value
