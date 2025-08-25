from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductVariant, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    ordering = ("name",)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    ordering = ("name",)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "seller", "category", "brand", "status", "is_active", "created_at")
    list_filter = ("status", "is_active", "category", "brand", "is_featured")
    search_fields = ("name", "slug", "sku", "seller__business_name")
    ordering = ("-created_at",)
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "is_primary", "order")
    list_filter = ("is_primary",)
    search_fields = ("product__name",)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "value", "sku", "stock_quantity", "is_active")
    list_filter = ("is_active", "name")
    search_fields = ("product__name", "sku")

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("product__name", "user__email", "user__name")
