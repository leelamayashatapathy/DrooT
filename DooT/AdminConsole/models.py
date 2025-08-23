from django.db import models
from Users.models import User, SellerProfile
from Products.models import Product
from Orders.models import Order
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid

class AdminProfile(models.Model):
    """Extended profile for admin users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    
    # Admin Information
    admin_level = models.CharField(max_length=20, choices=[
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('support', 'Support Staff'),
    ], default='moderator')
    
    # Permissions
    can_approve_sellers = models.BooleanField(default=False)
    can_approve_products = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_manage_payments = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_system = models.BooleanField(default=False)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.get_admin_level_display()}"

    @property
    def has_full_access(self):
        return self.admin_level == 'super_admin'

class SystemSettings(models.Model):
    """Global system configuration settings"""
    SETTING_TYPE_CHOICES = [
        ('general', 'General'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('commission', 'Commission'),
        ('notification', 'Notification'),
        ('security', 'Security'),
        ('seo', 'SEO'),
    ]

    # Basic Information
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPE_CHOICES)
    
    # Value Configuration
    value_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('file', 'File'),
    ])
    string_value = models.CharField(max_length=500, blank=True)
    integer_value = models.IntegerField(null=True, blank=True)
    decimal_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    json_value = models.JSONField(default=dict, blank=True)
    file_value = models.FileField(upload_to='system_settings/', blank=True, null=True)
    
    # Metadata
    is_public = models.BooleanField(default=False, help_text="Can be accessed by frontend")
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_settings')

    class Meta:
        ordering = ['setting_type', 'key']

    def __str__(self):
        return f"{self.key} - {self.name}"

    def get_value(self):
        """Get the actual value based on value_type"""
        if self.value_type == 'string':
            return self.string_value
        elif self.value_type == 'integer':
            return self.integer_value
        elif self.value_type == 'decimal':
            return self.decimal_value
        elif self.value_type == 'boolean':
            return self.boolean_value
        elif self.value_type == 'json':
            return self.json_value
        elif self.value_type == 'file':
            return self.file_value
        return None

    def set_value(self, value):
        """Set the value based on value_type"""
        if self.value_type == 'string':
            self.string_value = str(value)
        elif self.value_type == 'integer':
            self.integer_value = int(value)
        elif self.value_type == 'decimal':
            self.decimal_value = value
        elif self.value_type == 'boolean':
            self.boolean_value = bool(value)
        elif self.value_type == 'json':
            self.json_value = value
        elif self.value_type == 'file':
            self.file_value = value

class AuditLog(models.Model):
    """Track all admin actions for audit purposes"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('system_change', 'System Change'),
    ]

    # Log Information
    log_id = models.CharField(max_length=50, unique=True, blank=True)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    
    # Action Details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    
    # Generic Foreign Key for related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Changes
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Action duration in milliseconds")

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if not self.log_id:
            self.log_id = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admin_user.name} - {self.action} - {self.timestamp}"

class Dispute(models.Model):
    """Handle disputes between users, sellers, and platform"""
    DISPUTE_TYPE_CHOICES = [
        ('order', 'Order Dispute'),
        ('payment', 'Payment Dispute'),
        ('product', 'Product Dispute'),
        ('seller', 'Seller Dispute'),
        ('refund', 'Refund Dispute'),
        ('shipping', 'Shipping Dispute'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Dispute Information
    dispute_id = models.CharField(max_length=50, unique=True, blank=True)
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Parties Involved
    complainant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes_filed')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes_against', null=True, blank=True)
    
    # Related Objects
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='disputes', null=True, blank=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Resolution
    resolution = models.TextField(blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    evidence_files = models.JSONField(default=list, blank=True)
    admin_notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def save(self, *args, **kwargs):
        if not self.dispute_id:
            self.dispute_id = f"DISP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dispute {self.dispute_id} - {self.title}"

class DisputeMessage(models.Model):
    """Messages exchanged during dispute resolution"""
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispute_messages')
    
    # Message Content
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=[
        ('user_message', 'User Message'),
        ('admin_message', 'Admin Message'),
        ('system_message', 'System Message'),
    ], default='user_message')
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True)
    
    # Status
    is_internal = models.BooleanField(default=False, help_text="Internal admin notes not visible to users")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.name} - {self.dispute.dispute_id}"

class Report(models.Model):
    """User reports for products, sellers, or other content"""
    REPORT_TYPE_CHOICES = [
        ('product', 'Product'),
        ('seller', 'Seller'),
        ('review', 'Review'),
        ('user', 'User'),
        ('content', 'Content'),
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake/Scam'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
        ('escalated', 'Escalated'),
    ]

    # Report Information
    report_id = models.CharField(max_length=50, unique=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    reason = models.CharField(max_length=255)
    description = models.TextField()
    
    # Reporter
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    
    # Reported Content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolution_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Information
    evidence = models.JSONField(default=list, blank=True)
    priority = models.CharField(max_length=20, choices=Dispute.PRIORITY_CHOICES, default='medium')

    class Meta:
        ordering = ['-priority', '-created_at']

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report {self.report_id} - {self.reason}"

class SystemMaintenance(models.Model):
    """Track system maintenance and downtime"""
    MAINTENANCE_TYPE_CHOICES = [
        ('scheduled', 'Scheduled Maintenance'),
        ('emergency', 'Emergency Maintenance'),
        ('upgrade', 'System Upgrade'),
        ('backup', 'Backup/Restore'),
        ('security', 'Security Update'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Maintenance Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Impact
    affected_services = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=True, help_text="Show maintenance notice to users")
    
    # Notifications
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_maintenance')

    class Meta:
        ordering = ['-scheduled_start']

    def __str__(self):
        return f"{self.title} - {self.get_maintenance_type_display()}"

    @property
    def is_active(self):
        now = timezone.now()
        return (
            self.status == 'in_progress' and
            self.actual_start and
            (not self.actual_end or self.actual_end > now)
        )

    @property
    def duration_minutes(self):
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 60
        return None
