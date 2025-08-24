from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    # Seller endpoints
    path('register/', views.SellerRegisterView.as_view(), name='register'),
    path('profile/', views.SellerProfileView.as_view(), name='profile'),
    path('dashboard/', views.SellerDashboardView.as_view(), name='dashboard'),
    path('products/', views.SellerProductListView.as_view(), name='product-list'),
    path('products/create/', views.SellerProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', views.SellerProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', views.SellerProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.SellerProductDeleteView.as_view(), name='product-delete'),
    path('orders/', views.SellerOrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.SellerOrderDetailView.as_view(), name='order-detail'),
    path('analytics/', views.SellerAnalyticsView.as_view(), name='analytics'),
]
