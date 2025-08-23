from rest_framework import serializers
from .models import Coupon, CouponUsage, Discount, Promotion, Campaign, ReferralProgram, Referral
from django.utils import timezone

class CouponSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    remaining_uses = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_usage_count(self, obj):
        return obj.usage.count()
    
    def get_remaining_uses(self, obj):
        if obj.max_uses:
            return max(0, obj.max_uses - obj.usage.count())
        return None

class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'min_order_amount', 
                 'max_uses', 'valid_from', 'valid_until', 'is_active', 'description']
    
    def validate(self, attrs):
        # Validate date range
        if attrs.get('valid_from') and attrs.get('valid_until'):
            if attrs['valid_from'] >= attrs['valid_until']:
                raise serializers.ValidationError("Valid from date must be before valid until date")
        
        # Validate discount value
        if attrs['discount_type'] == 'percentage' and attrs['discount_value'] > 100:
            raise serializers.ValidationError("Percentage discount cannot exceed 100%")
        
        return attrs

class CouponUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['is_active', 'description', 'valid_from', 'valid_until', 'max_uses']

class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
        read_only_fields = ['id', 'used_at', 'created_at']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DiscountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['name', 'discount_type', 'discount_value', 'min_order_amount', 
                 'max_discount', 'is_active', 'description', 'valid_from', 'valid_until']
    
    def validate(self, attrs):
        # Validate discount value
        if attrs['discount_type'] == 'percentage' and attrs['discount_value'] > 100:
            raise serializers.ValidationError("Percentage discount cannot exceed 100%")
        
        return attrs

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class PromotionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['name', 'description', 'promotion_type', 'discount', 'conditions', 
                 'valid_from', 'valid_until', 'is_active', 'target_audience']

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'campaign_type', 'budget', 'start_date', 
                 'end_date', 'target_audience', 'channels', 'is_active']

class ReferralProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralProgram
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReferralProgramCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralProgram
        fields = ['name', 'description', 'referrer_reward', 'referee_reward', 
                 'min_purchase_amount', 'is_active', 'valid_from', 'valid_until']

class ReferralSerializer(serializers.ModelSerializer):
    referrer_name = serializers.CharField(source='referrer.name', read_only=True)
    referee_name = serializers.CharField(source='referee.name', read_only=True)
    
    class Meta:
        model = Referral
        fields = '__all__'
        read_only_fields = ['id', 'referral_code', 'created_at', 'updated_at']

class ReferralCreateSerializer(serializers.Serializer):
    referee_email = serializers.EmailField()
    
    def validate_referee_email(self, value):
        # Check if referee already exists
        from Users.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

class CouponValidationSerializer(serializers.Serializer):
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value, is_active=True)
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")
    
    def validate(self, attrs):
        coupon = attrs['code']
        order_amount = attrs['order_amount']
        
        # Check if coupon is expired
        if coupon.valid_until and timezone.now() > coupon.valid_until:
            raise serializers.ValidationError("Coupon has expired")
        
        # Check if coupon is not yet valid
        if coupon.valid_from and timezone.now() < coupon.valid_from:
            raise serializers.ValidationError("Coupon is not yet valid")
        
        # Check minimum order amount
        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            raise serializers.ValidationError(f"Minimum order amount is ${coupon.min_order_amount}")
        
        # Check usage limit
        if coupon.max_uses and coupon.usage.count() >= coupon.max_uses:
            raise serializers.ValidationError("Coupon usage limit reached")
        
        return attrs

class PromotionSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    promotion_type = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
