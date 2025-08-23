from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Products.models import Product, Category
from Users.models import User, SellerProfile
from django.utils import timezone
import uuid

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]

    APPLICABLE_TO_CHOICES = [
        ('all', 'All Products'),
        ('categories', 'Specific Categories'),
        ('products', 'Specific Products'),
        ('sellers', 'Specific Sellers'),
    ]

    # Basic Information
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Discount Configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usage Limits
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    
    # Applicability
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE_TO_CHOICES, default='all')
    categories = models.ManyToManyField(Category, blank=True, related_name='coupons')
    products = models.ManyToManyField(Product, blank=True, related_name='coupons')
    sellers = models.ManyToManyField(SellerProfile, blank=True, related_name='coupons')
    
    # Order Requirements
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # User Restrictions
    first_time_users_only = models.BooleanField(default=False)
    user_groups = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_coupons')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )

    @property
    def is_expired(self):
        return timezone.now() > self.valid_until

    def can_use_for_user(self, user, order_value=0):
        """Check if user can use this coupon"""
        if not self.is_valid:
            return False, "Coupon is not valid"
        
        if order_value < self.min_order_value:
            return False, f"Minimum order value is {self.min_order_value}"
        
        if self.max_order_value and order_value > self.max_order_value:
            return False, f"Maximum order value is {self.max_order_value}"
        
        if self.first_time_users_only and user.orders.exists():
            return False, "Coupon is for first-time users only"
        
        # Check usage per user
        user_usage = CouponUsage.objects.filter(coupon=self, user=user).count()
        if user_usage >= self.max_uses_per_user:
            return False, "Maximum usage limit reached for this user"
        
        return True, "Valid"

    def calculate_discount(self, order_value):
        """Calculate discount amount for given order value"""
        if self.discount_type == 'percentage':
            discount = (order_value * self.discount_value) / 100
        elif self.discount_type == 'fixed':
            discount = self.discount_value
        else:  # free_shipping
            discount = 0  # Will be handled separately
        
        if self.max_discount:
            discount = min(discount, self.max_discount)
        
        return discount

class CouponUsage(models.Model):
    """Track coupon usage by users"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey('Orders.Order', on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['coupon', 'order']

    def __str__(self):
        return f"{self.coupon.code} used by {self.user.name}"

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bundle', 'Bundle Discount'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    
    # Discount Configuration
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Applicability
    products = models.ManyToManyField(Product, related_name='discounts')
    categories = models.ManyToManyField(Category, related_name='discounts')
    
    # Conditions
    min_quantity = models.PositiveIntegerField(default=1)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()}"

    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until

class Promotion(models.Model):
    PROMOTION_TYPE_CHOICES = [
        ('flash_sale', 'Flash Sale'),
        ('seasonal', 'Seasonal Sale'),
        ('clearance', 'Clearance Sale'),
        ('new_user', 'New User Offer'),
        ('loyalty', 'Loyalty Reward'),
        ('referral', 'Referral Bonus'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    description = models.TextField()
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPE_CHOICES)
    
    # Applicability
    products = models.ManyToManyField(Product, blank=True, related_name='promotions')
    categories = models.ManyToManyField(Category, blank=True, related_name='promotions')
    sellers = models.ManyToManyField(SellerProfile, blank=True, related_name='promotions')
    
    # Validity
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Display
    banner_image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    banner_text = models.CharField(max_length=255, blank=True)
    priority = models.PositiveIntegerField(default=0, help_text="Higher priority promotions are shown first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_promotions')

    class Meta:
        ordering = ['-priority', '-start_date']

    def __str__(self):
        return f"{self.name} - {self.get_promotion_type_display()}"

    @property
    def is_active_now(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class Campaign(models.Model):
    CAMPAIGN_TYPE_CHOICES = [
        ('email', 'Email Campaign'),
        ('sms', 'SMS Campaign'),
        ('push', 'Push Notification Campaign'),
        ('banner', 'Banner Campaign'),
        ('social', 'Social Media Campaign'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    description = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Content
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Targeting
    target_audience = models.JSONField(default=dict, help_text="Targeting criteria in JSON format")
    user_segments = models.JSONField(default=list, blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Statistics
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_converted = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_campaigns')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_campaign_type_display()}"

    @property
    def open_rate(self):
        if self.total_sent == 0:
            return 0
        return (self.total_opened / self.total_sent) * 100

    @property
    def click_rate(self):
        if self.total_sent == 0:
            return 0
        return (self.total_clicked / self.total_sent) * 100

    @property
    def conversion_rate(self):
        if self.total_sent == 0:
            return 0
        return (self.total_converted / self.total_sent) * 100

class ReferralProgram(models.Model):
    """Referral program for users to earn rewards"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Reward Configuration
    referrer_reward_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage of Order'),
        ('fixed', 'Fixed Amount'),
        ('points', 'Loyalty Points'),
    ])
    referrer_reward_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    referee_reward_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Discount'),
        ('free_shipping', 'Free Shipping'),
    ])
    referee_reward_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Conditions
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_referrals_per_user = models.PositiveIntegerField(null=True, blank=True)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Referral Program"

class Referral(models.Model):
    """Track user referrals"""
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')
    referral_code = models.CharField(max_length=50, unique=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    # Rewards
    referrer_reward_claimed = models.BooleanField(default=False)
    referee_reward_claimed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['referrer', 'referee']

    def __str__(self):
        return f"{self.referrer.name} -> {self.referee.name}"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = f"REF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
