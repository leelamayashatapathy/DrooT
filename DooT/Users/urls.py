from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Phone Verification
    path('verify-phone/', views.verify_phone, name='verify-phone'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),
    
    # Seller Profile
    path('seller/profile/', views.SellerProfileView.as_view(), name='seller-profile'),
    path('seller/profile/<int:seller_id>/', views.SellerProfileDetailView.as_view(), name='seller-profile-detail'),
    
    # Admin User Management
    path('admin/users/', views.UserListView.as_view(), name='user-list'),
    path('admin/users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
]
