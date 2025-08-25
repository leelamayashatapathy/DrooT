from django.contrib import admin
from .models import PaymentMethod, Payment, Refund, PayoutRequest, Commission

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "payment_type", "is_active")
  list_filter = ("is_active", "payment_type")
  search_fields = ("name",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
  list_display = ("id", "payment_id", "order", "user", "amount", "status", "created_at")
  list_filter = ("status", "created_at")
  search_fields = ("payment_id", "order__order_number", "user__email")

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
  list_display = ("id", "refund_id", "payment", "order", "user", "refund_amount", "status", "created_at")
  list_filter = ("status", "created_at")
  search_fields = ("refund_id", "payment__payment_id", "order__order_number", "user__email")

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
  list_display = ("id", "payout_id", "seller", "requested_amount", "status", "created_at")
  list_filter = ("status", "created_at")
  search_fields = ("payout_id", "seller__business_name")

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
  list_display = ("id", "seller", "category", "commission_type", "commission_value", "is_active")
  list_filter = ("commission_type", "is_active")
  search_fields = ("seller__business_name", "category__name")
