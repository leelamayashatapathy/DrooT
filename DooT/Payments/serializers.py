from rest_framework import serializers
from .models import PaymentMethod, Payment, Refund, PayoutRequest, Commission

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'payment_id', 'user', 'order', 'created_at', 'updated_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['order', 'payment_method', 'amount', 'notes']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['processing_fee'] = 0.00  # Calculate based on payment method
        return super().create(validated_data)

class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['status', 'transaction_id', 'failure_reason', 'notes']

class RefundSerializer(serializers.ModelSerializer):
    payment_id = serializers.CharField(source='payment.payment_id', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ['id', 'refund_id', 'payment', 'order', 'user', 'created_at', 'updated_at']

class RefundCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['payment', 'refund_amount', 'refund_type', 'reason']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['order'] = validated_data['payment'].order
        return super().create(validated_data)

class RefundUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['status', 'admin_notes']

class PayoutRequestSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = PayoutRequest
        fields = '__all__'
        read_only_fields = ['id', 'payout_id', 'seller', 'status', 'created_at', 'updated_at']

class PayoutRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = ['requested_amount', 'bank_account_number', 'bank_ifsc_code', 'account_holder_name']
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user.seller_profile
        return super().create(validated_data)

class PayoutRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = ['status', 'admin_notes', 'rejection_reason']

class CommissionSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Commission
        fields = '__all__'

class PaymentProcessSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, attrs):
        # Add validation logic here
        return attrs

class PaymentWebhookSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    status = serializers.CharField()
    transaction_id = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False)
    metadata = serializers.JSONField(required=False)
