from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from .models import User, SellerProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    SellerProfileSerializer, SellerProfileCreateSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            # In a real application, send password reset email here
            return Response({'message': 'Password reset email sent'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # In a real application, verify token and reset password here
            return Response({'message': 'Password reset successful'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = SellerProfile.objects.get(user=request.user)
            serializer = SellerProfileSerializer(profile)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response({'message': 'Seller profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        if hasattr(request.user, 'seller_profile'):
            return Response({'message': 'Seller profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SellerProfileCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save()
            request.user.is_seller = True
            request.user.save()
            return Response(SellerProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            profile = SellerProfile.objects.get(user=request.user)
            serializer = SellerProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SellerProfile.DoesNotExist:
            return Response({'message': 'Seller profile not found'}, status=status.HTTP_404_NOT_FOUND)

class SellerProfileDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, seller_id):
        try:
            profile = SellerProfile.objects.get(id=seller_id, is_active=True)
            serializer = SellerProfileSerializer(profile)
            return Response(serializer.data)
        except SellerProfile.DoesNotExist:
            return Response({'message': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)

class UserListView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone(request):
    """Verify phone number with OTP"""
    otp = request.data.get('otp')
    if not otp:
        return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    if user.otp == otp:
        user.is_phone_verified = True
        user.save()
        return Response({'message': 'Phone verified successfully'})
    else:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_otp(request):
    """Resend OTP for phone verification"""
    # In a real application, generate and send new OTP here
    return Response({'message': 'OTP resent successfully'})
