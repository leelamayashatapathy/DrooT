from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart Management
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    
    # Orders
    path('', views.OrderListView.as_view(), name='order-list'),
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='order-update'),
    path('<int:order_id>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    path('<int:order_id>/tracking/', views.OrderTrackingView.as_view(), name='order-tracking'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Return Requests
    path('returns/', views.ReturnRequestListView.as_view(), name='return-list'),
    path('returns/create/', views.ReturnRequestCreateView.as_view(), name='return-create'),
    path('returns/<int:pk>/', views.ReturnRequestDetailView.as_view(), name='return-detail'),
    path('returns/<int:pk>/update/', views.ReturnRequestUpdateView.as_view(), name='return-update'),
    
    # Statistics
    path('statistics/', views.order_statistics, name='order-statistics'),
]
