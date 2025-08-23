from django.db import models
from Orders.models import Order
from django.core.validators import MinValueValidator
import uuid

class ShippingZone(models.Model):
    name = models.CharField(max_length=100)
    countries = models.JSONField(default=list)  # List of country codes
    states = models.JSONField(default=list)    # List of state codes
    cities = models.JSONField(default=list)    # List of city names
    zip_codes = models.JSONField(default=list) # List of zip code patterns
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_address_in_zone(self, country, state=None, city=None, zip_code=None):
        """Check if an address falls within this shipping zone"""
        if country and country not in self.countries:
            return False
        if state and state not in self.states:
            return False
        if city and city not in self.cities:
            return False
        if zip_code:
            for pattern in self.zip_codes:
                if zip_code.startswith(pattern):
                    return True
            return False
        return True

class ShippingMethod(models.Model):
    METHOD_TYPE_CHOICES = [
        ('standard', 'Standard Shipping'),
        ('express', 'Express Shipping'),
        ('overnight', 'Overnight Shipping'),
        ('same_day', 'Same Day Delivery'),
        ('pickup', 'Store Pickup'),
    ]

    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPE_CHOICES)
    description = models.TextField(blank=True)
    estimated_days = models.PositiveIntegerField(help_text="Estimated delivery time in days")
    is_active = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='shipping_methods/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ShippingRate(models.Model):
    shipping_zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='shipping_rates')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name='shipping_rates')
    
    # Pricing
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    per_item_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Weight and quantity limits
    min_weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    min_items = models.PositiveIntegerField(default=1)
    max_items = models.PositiveIntegerField(null=True, blank=True)
    
    # Order value limits
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Free shipping conditions
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['shipping_zone', 'shipping_method']

    def __str__(self):
        return f"{self.shipping_zone.name} - {self.shipping_method.name}"

    def calculate_shipping_cost(self, order_weight, item_count, order_value):
        """Calculate shipping cost based on weight, items, and order value"""
        # Check if order qualifies for free shipping
        if self.free_shipping_threshold and order_value >= self.free_shipping_threshold:
            return 0.00
        
        # Check weight and item limits
        if order_weight < self.min_weight or (self.max_weight and order_weight > self.max_weight):
            return None
        
        if item_count < self.min_items or (self.max_items and item_count > self.max_items):
            return None
        
        # Check order value limits
        if order_value < self.min_order_value or (self.max_order_value and order_value > self.max_order_value):
            return None
        
        # Calculate cost
        cost = self.base_rate
        cost += (order_weight * self.per_kg_rate)
        cost += (item_count * self.per_item_rate)
        
        return max(cost, 0.00)

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('returned', 'Returned'),
    ]

    # Shipment Information
    shipment_id = models.CharField(max_length=50, unique=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    shipping_rate = models.ForeignKey(ShippingRate, on_delete=models.CASCADE)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(blank=True)
    
    # Shipping Details
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    package_weight = models.DecimalField(max_digits=8, decimal_places=2)
    package_dimensions = models.CharField(max_length=100, blank=True)
    
    # Address Information
    origin_address = models.TextField()
    destination_address = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.shipment_id:
            self.shipment_id = f"SHIP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment {self.shipment_id} - {self.order.order_number}"

class ShipmentTracking(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.shipment_id} - {self.status} at {self.timestamp}"

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing Address'),
        ('shipping', 'Shipping Address'),
        ('both', 'Billing & Shipping'),
    ]

    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='both')
    
    # Address Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=15)
    phone = models.CharField(max_length=20)
    
    # Additional Information
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per type per user
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type__in=[self.address_type, 'both'],
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([self.city, self.state, self.country, self.zip_code])
        return ", ".join(filter(None, address_parts))
