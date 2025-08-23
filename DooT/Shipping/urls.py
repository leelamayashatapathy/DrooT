from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Shipping Zones and Methods
    path('zones/', views.ShippingZoneListView.as_view(), name='zone-list'),
    path('zones/<int:pk>/', views.ShippingZoneDetailView.as_view(), name='zone-detail'),
    path('methods/', views.ShippingMethodListView.as_view(), name='method-list'),
    path('methods/<int:pk>/', views.ShippingMethodDetailView.as_view(), name='method-detail'),
    path('rates/', views.ShippingRateListView.as_view(), name='rate-list'),
    
    # Address Management
    path('addresses/', views.AddressListView.as_view(), name='address-list'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address-create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/update/', views.AddressUpdateView.as_view(), name='address-update'),
    
    # Shipments
    path('shipments/', views.ShipmentListView.as_view(), name='shipment-list'),
    path('shipments/create/', views.ShipmentCreateView.as_view(), name='shipment-create'),
    path('<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('<int:pk>/update/', views.ShipmentUpdateView.as_view(), name='shipment-update'),
    path('<int:shipment_id>/tracking/', views.ShipmentTrackingView.as_view(), name='shipment-tracking'),
    
    # Shipping Calculator
    path('calculate/', views.ShippingCalculatorView.as_view(), name='shipping-calculator'),
    
    # Admin Functions
    path('admin/update-rates/', views.update_shipping_rates, name='update-rates'),
    path('admin/statistics/', views.shipping_statistics, name='shipping-statistics'),
]
