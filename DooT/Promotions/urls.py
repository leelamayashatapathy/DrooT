from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/create/', views.CouponCreateView.as_view(), name='coupon-create'),
    path('coupons/<int:pk>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/<int:pk>/update/', views.CouponUpdateView.as_view(), name='coupon-update'),
    path('coupons/validate/', views.validate_coupon, name='validate-coupon'),
    
    # Coupon Usage
    path('coupon-usage/', views.CouponUsageListView.as_view(), name='coupon-usage-list'),
    path('coupon-usage/<int:pk>/', views.CouponUsageDetailView.as_view(), name='coupon-usage-detail'),
    
    # Discounts
    path('discounts/', views.DiscountListView.as_view(), name='discount-list'),
    path('discounts/create/', views.DiscountCreateView.as_view(), name='discount-create'),
    path('discounts/<int:pk>/', views.DiscountDetailView.as_view(), name='discount-detail'),
    path('discounts/<int:pk>/update/', views.DiscountUpdateView.as_view(), name='discount-update'),
    
    # Promotions
    path('', views.PromotionListView.as_view(), name='promotion-list'),
    path('create/', views.PromotionCreateView.as_view(), name='promotion-create'),
    path('<int:pk>/', views.PromotionDetailView.as_view(), name='promotion-detail'),
    path('<int:pk>/update/', views.PromotionUpdateView.as_view(), name='promotion-update'),
    path('search/', views.PromotionSearchView.as_view(), name='promotion-search'),
    
    # Campaigns
    path('campaigns/', views.CampaignListView.as_view(), name='campaign-list'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign-create'),
    path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<int:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign-update'),
    
    # Referral Programs
    path('referrals/', views.ReferralProgramListView.as_view(), name='referral-program-list'),
    path('referrals/create/', views.ReferralProgramCreateView.as_view(), name='referral-program-create'),
    path('referrals/<int:pk>/', views.ReferralProgramDetailView.as_view(), name='referral-program-detail'),
    path('referrals/<int:pk>/update/', views.ReferralProgramUpdateView.as_view(), name='referral-program-update'),
    
    # Referrals
    path('referrals/users/', views.ReferralListView.as_view(), name='referral-list'),
    path('referrals/users/create/', views.ReferralCreateView.as_view(), name='referral-create'),
    path('referrals/users/<int:pk>/', views.ReferralDetailView.as_view(), name='referral-detail'),
    
    # Statistics
    path('statistics/', views.promotion_statistics, name='promotion-statistics'),
]
