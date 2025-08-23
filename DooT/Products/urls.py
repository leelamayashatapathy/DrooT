from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories and Brands
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('brands/<int:pk>/', views.BrandDetailView.as_view(), name='brand-detail'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Seller Product Management
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('update/<int:pk>/', views.ProductUpdateView.as_view(), name='product-update'),
    path('delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('seller/products/', views.SellerProductListView.as_view(), name='seller-products'),
    
    # Product Images and Variants
    path('<int:product_id>/images/', views.ProductImageUploadView.as_view(), name='product-images'),
    path('<int:product_id>/variants/', views.ProductVariantListView.as_view(), name='product-variants'),
    path('<int:product_id>/variants/create/', views.ProductVariantCreateView.as_view(), name='product-variant-create'),
    
    # Reviews
    path('<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='product-reviews'),
    path('<int:product_id>/reviews/create/', views.ProductReviewCreateView.as_view(), name='product-review-create'),
    
    # Admin Actions
    path('admin/<int:product_id>/toggle-featured/', views.toggle_product_featured, name='toggle-featured'),
    path('admin/<int:product_id>/approve/', views.approve_product, name='approve-product'),
    path('admin/<int:product_id>/reject/', views.reject_product, name='reject-product'),
]
