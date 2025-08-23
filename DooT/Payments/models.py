from django.db import models
from Users.models import User, SellerProfile
from Orders.models import Order
from django.utils import timezone
import uuid

class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    name = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='payment_methods/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    # Payment Information
    payment_id = models.CharField(max_length=50, unique=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Financial Information
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_response = models.JSONField(default=dict, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        if not self.net_amount:
            self.net_amount = self.amount - self.processing_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.order.order_number}"

    @property
    def is_successful(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled']

class Refund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REFUND_TYPE_CHOICES = [
        ('full', 'Full Refund'),
        ('partial', 'Partial Refund'),
    ]

    # Refund Information
    refund_id = models.CharField(max_length=50, unique=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refunds')
    
    # Financial Information
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPE_CHOICES)
    processing_fee_refund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status & Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField()
    admin_notes = models.TextField(blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Refund {self.refund_id} - {self.payment.payment_id}"

class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    # Payout Information
    payout_id = models.CharField(max_length=50, unique=True, blank=True)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='payout_requests')
    
    # Financial Information
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Bank Details
    bank_account_number = models.CharField(max_length=30)
    bank_ifsc_code = models.CharField(max_length=20)
    account_holder_name = models.CharField(max_length=255)
    
    # Status & Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payout_id:
            self.payout_id = f"PAYOUT-{uuid.uuid4().hex[:8].upper()}"
        if not self.net_amount:
            self.net_amount = self.requested_amount - self.processing_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payout {self.payout_id} - {self.seller.business_name}"

class Commission(models.Model):
    COMMISSION_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    # Commission Configuration
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='commissions', null=True, blank=True)
    category = models.ForeignKey('Products.Category', on_delete=models.CASCADE, related_name='commissions', null=True, blank=True)
    
    # Commission Details
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES)
    commission_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['seller', 'category']]

    def __str__(self):
        if self.seller and self.category:
            return f"{self.seller.business_name} - {self.category.name}"
        elif self.seller:
            return f"{self.seller.business_name} - Default"
        elif self.category:
            return f"Default - {self.category.name}"
        return "Default Commission"

    def calculate_commission(self, order_amount):
        """Calculate commission for a given order amount"""
        if self.commission_type == 'percentage':
            commission = (order_amount * self.commission_value) / 100
        else:
            commission = self.commission_value
        
        if self.max_commission:
            commission = min(commission, self.max_commission)
        
        return commission
