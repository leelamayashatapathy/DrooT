from django.contrib import admin
from .models import User, SellerProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "is_seller", "is_active", "is_staff", "created_at")
    list_filter = ("is_seller", "is_active", "is_staff", "is_admin", "is_superuser")
    search_fields = ("email", "name", "phone")
    ordering = ("-created_at",)

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "business_name", "user", "is_verified", "is_active", "created_at")
    list_filter = ("is_verified", "is_active", "city", "state")
    search_fields = ("business_name", "user__email", "user__name", "phone", "gst_number")
    ordering = ("-created_at",)

# Register your models here.
