from django.db import models
from Users.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid

class NotificationTemplate(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]

    TRIGGER_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('payment_success', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('product_approved', 'Product Approved'),
        ('product_rejected', 'Product Rejected'),
        ('seller_approved', 'Seller Approved'),
        ('seller_rejected', 'Seller Rejected'),
        ('low_stock', 'Low Stock Alert'),
        ('price_change', 'Price Change'),
        ('new_review', 'New Review'),
        ('refund_request', 'Refund Request'),
        ('payout_processed', 'Payout Processed'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    
    # Content
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    html_template = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="Delay in minutes before sending")
    max_retries = models.PositiveIntegerField(default=3)
    
    # Variables that can be used in templates
    available_variables = models.JSONField(default=list, help_text="List of available template variables")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_trigger_display()}"

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Notification Information
    notification_id = models.CharField(max_length=50, unique=True, blank=True)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='notifications')
    
    # Recipients
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Content
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Sending Configuration
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Generic Foreign Key for related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional Information
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def save(self, *args, **kwargs):
        if not self.notification_id:
            self.notification_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        recipient = self.user.name if self.user else self.email
        return f"Notification {self.notification_id} to {recipient}"

    @property
    def is_scheduled(self):
        return self.scheduled_at and self.scheduled_at > timezone.now()

    @property
    def can_retry(self):
        return self.status == 'failed' and self.retry_count < self.template.max_retries

class UserNotification(models.Model):
    """In-app notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Notification Type
    notification_type = models.CharField(max_length=50, default='info')
    icon = models.CharField(max_length=50, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Action
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Generic Foreign Key for related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.name}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

class EmailLog(models.Model):
    """Log of all email notifications sent"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    
    # Status
    status = models.CharField(max_length=20, choices=Notification.STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Email Details
    message_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"

class SMSLog(models.Model):
    """Log of all SMS notifications sent"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='sms_logs')
    recipient_phone = models.CharField(max_length=20)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=Notification.STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # SMS Details
    message_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # Cost Information
    cost = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.status}"

class NotificationPreference(models.Model):
    """User preferences for different types of notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email Preferences
    email_order_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    
    # SMS Preferences
    sms_order_updates = models.BooleanField(default=False)
    sms_promotions = models.BooleanField(default=False)
    sms_delivery_alerts = models.BooleanField(default=True)
    
    # Push Notification Preferences
    push_order_updates = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=True)
    push_price_drops = models.BooleanField(default=True)
    
    # Frequency
    email_frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ], default='immediate')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user']

    def __str__(self):
        return f"Notification Preferences - {self.user.name}"
