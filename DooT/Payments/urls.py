from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    
    # Payments
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment-update'),
    
    # Payment Processing
    path('process/', views.process_payment, name='process-payment'),
    path('webhook/', views.payment_webhook, name='payment-webhook'),
    path('statistics/', views.payment_statistics, name='payment-statistics'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund-list'),
    path('refunds/create/', views.RefundCreateView.as_view(), name='refund-create'),
    path('refunds/<int:pk>/', views.RefundDetailView.as_view(), name='refund-detail'),
    path('refunds/<int:pk>/update/', views.RefundUpdateView.as_view(), name='refund-update'),
    path('request-refund/<str:payment_id>/', views.request_refund, name='request-refund'),
    
    # Payout Requests
    path('payouts/', views.PayoutRequestListView.as_view(), name='payout-list'),
    path('payouts/create/', views.PayoutRequestCreateView.as_view(), name='payout-create'),
    path('payouts/<int:pk>/', views.PayoutRequestDetailView.as_view(), name='payout-detail'),
    path('payouts/<int:pk>/update/', views.PayoutRequestUpdateView.as_view(), name='payout-update'),
    
    # Commissions (Admin)
    path('commissions/', views.CommissionListView.as_view(), name='commission-list'),
    path('commissions/create/', views.CommissionCreateView.as_view(), name='commission-create'),
    path('commissions/<int:pk>/', views.CommissionDetailView.as_view(), name='commission-detail'),
]
