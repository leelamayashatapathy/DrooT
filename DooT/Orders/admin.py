from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, OrderStatus, ReturnRequest

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__name")
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "variant", "quantity", "added_at")
    search_fields = ("product__name", "cart__user__email")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "user", "seller", "status", "payment_status", "total_amount", "created_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "user__email", "seller__business_name")
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "variant", "quantity", "unit_price", "total_price")
    search_fields = ("order__order_number", "product__name")

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "created_at", "updated_by")
    list_filter = ("status",)
    search_fields = ("order__order_number",)

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "status", "refund_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order__order_number", "user__email")
