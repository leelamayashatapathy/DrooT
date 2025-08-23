from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import AdminProfile, SystemSettings, AuditLog, Dispute, DisputeMessage, Report, SystemMaintenance
from .serializers import (
    AdminProfileSerializer, AdminProfileCreateSerializer, SystemSettingsSerializer,
    SystemSettingsUpdateSerializer, AuditLogSerializer, DisputeSerializer,
    DisputeCreateSerializer, DisputeUpdateSerializer, DisputeMessageSerializer,
    DisputeMessageCreateSerializer, ReportSerializer, ReportCreateSerializer,
    ReportUpdateSerializer, SystemMaintenanceSerializer, SystemMaintenanceCreateSerializer,
    SystemMaintenanceUpdateSerializer, DashboardStatisticsSerializer,
    UserManagementSerializer, ContentModerationSerializer
)

User = get_user_model()

# Keep generics for simple listing and retrieval
class AdminProfileListView(generics.ListAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['admin_level', 'department', 'is_active']
    ordering_fields = ['created_at', 'user__name']
    ordering = ['-created_at']

class AdminProfileDetailView(generics.RetrieveAPIView):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class SystemSettingsListView(generics.ListAPIView):
    queryset = SystemSettings.objects.filter(is_public=True)
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

class SystemSettingsDetailView(generics.RetrieveAPIView):
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'admin', 'object_type']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']

class DisputeListView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'dispute_type', 'user', 'seller']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

class DisputeDetailView(generics.RetrieveAPIView):
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAdminUser]

class DisputeMessageListView(generics.ListAPIView):
    serializer_class = DisputeMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        dispute_id = self.kwargs.get('dispute_id')
        return DisputeMessage.objects.filter(dispute_id=dispute_id)

class ReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'report_type', 'reporter', 'reported_user']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

class ReportDetailView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

class SystemMaintenanceListView(generics.ListAPIView):
    serializer_class = SystemMaintenanceSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'maintenance_type', 'admin']
    ordering_fields = ['scheduled_start', 'created_at']
    ordering = ['-scheduled_start']

class SystemMaintenanceDetailView(generics.RetrieveAPIView):
    queryset = SystemMaintenance.objects.all()
    serializer_class = SystemMaintenanceSerializer
    permission_classes = [permissions.IsAdminUser]

# Convert to APIView for custom operations
class AdminProfileCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create admin profile with custom validation"""
        serializer = AdminProfileCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check if user already has admin profile
                if AdminProfile.objects.filter(user=request.user).exists():
                    return Response({
                        'error': 'User already has an admin profile'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate permissions
                permissions = serializer.validated_data.get('permissions', [])
                if not self._validate_permissions(permissions):
                    return Response({
                        'error': 'Invalid permissions specified'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                admin_profile = serializer.save()
                
                return Response({
                    'message': 'Admin profile created successfully',
                    'admin_profile': AdminProfileSerializer(admin_profile).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating admin profile: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _validate_permissions(self, permissions):
        """Validate admin permissions"""
        valid_permissions = [
            'user_management', 'product_moderation', 'order_management',
            'payment_management', 'dispute_resolution', 'system_settings',
            'analytics', 'content_moderation'
        ]
        return all(perm in valid_permissions for perm in permissions)

class SystemSettingsUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get system setting and check access"""
        try:
            return SystemSettings.objects.get(id=pk)
        except SystemSettings.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update system setting with custom validation"""
        setting = self.get_object(pk)
        if not setting:
            return Response({'error': 'System setting not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SystemSettingsUpdateSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Validate setting value based on setting type
                if not self._validate_setting_value(setting, serializer.validated_data.get('value')):
                    return Response({
                        'error': f'Invalid value for setting type: {setting.setting_type}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                
                # Log the change
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user,
                    action='update',
                    object_type='system_setting',
                    object_id=setting.id,
                    details=f'Updated {setting.key} to {serializer.validated_data.get("value")}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'System setting updated successfully',
                    'setting': SystemSettingsSerializer(setting).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating system setting: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _validate_setting_value(self, setting, value):
        """Validate setting value based on type"""
        if setting.value_type == 'boolean':
            return isinstance(value, bool)
        elif setting.value_type == 'integer':
            return isinstance(value, int)
        elif setting.value_type == 'decimal':
            return isinstance(value, (int, float))
        elif setting.value_type == 'string':
            return isinstance(value, str)
        elif setting.value_type == 'json':
            return isinstance(value, dict)
        return True

class DisputeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create dispute with custom validation"""
        serializer = DisputeCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                order = serializer.validated_data.get('order')
                
                # Check if user has access to this order
                if order.user != request.user and not hasattr(request.user, 'admin_profile'):
                    return Response({
                        'error': 'You can only create disputes for your own orders'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Check if dispute already exists for this order
                if Dispute.objects.filter(order=order).exists():
                    return Response({
                        'error': 'Dispute already exists for this order'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create dispute
                dispute = serializer.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user if hasattr(request.user, 'admin_profile') else None,
                    action='create',
                    object_type='dispute',
                    object_id=dispute.id,
                    details=f'Created dispute for order {order.order_number}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'Dispute created successfully',
                    'dispute': DisputeSerializer(dispute).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating dispute: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisputeUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get dispute and check access"""
        try:
            return Dispute.objects.get(id=pk)
        except Dispute.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update dispute with custom logic"""
        dispute = self.get_object(pk)
        if not dispute:
            return Response({'error': 'Dispute not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DisputeUpdateSerializer(dispute, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Update dispute
                serializer.save()
                
                # If resolved, set resolved_at
                if serializer.validated_data.get('status') == 'resolved':
                    dispute.resolved_at = timezone.now()
                    dispute.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user,
                    action='update',
                    object_type='dispute',
                    object_id=dispute.id,
                    details=f'Updated dispute status to {serializer.validated_data.get("status")}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'Dispute updated successfully',
                    'dispute': DisputeSerializer(dispute).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating dispute: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisputeMessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create dispute message with custom validation"""
        serializer = DisputeMessageCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                dispute = serializer.validated_data.get('dispute')
                
                # Check if user has access to this dispute
                if dispute.user != request.user and not hasattr(request.user, 'admin_profile'):
                    return Response({
                        'error': 'You can only add messages to disputes you are involved in'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Create message
                message = serializer.save()
                
                return Response({
                    'message': 'Dispute message created successfully',
                    'dispute_message': DisputeMessageSerializer(message).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating dispute message: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create report with custom validation"""
        serializer = ReportCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                reported_user = serializer.validated_data.get('reported_user')
                
                # Check if user is reporting themselves
                if reported_user == request.user:
                    return Response({
                        'error': 'You cannot report yourself'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if report already exists
                if Report.objects.filter(
                    reporter=request.user,
                    reported_user=reported_user,
                    status__in=['pending', 'investigating']
                ).exists():
                    return Response({
                        'error': 'You already have a pending report for this user'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create report
                report = serializer.save()
                
                return Response({
                    'message': 'Report created successfully',
                    'report': ReportSerializer(report).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating report: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get report and check access"""
        try:
            return Report.objects.get(id=pk)
        except Report.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update report with custom logic"""
        report = self.get_object(pk)
        if not report:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReportUpdateSerializer(report, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Update report
                serializer.save()
                
                # If resolved, set resolved_at
                if serializer.validated_data.get('status') == 'resolved':
                    report.resolved_at = timezone.now()
                    report.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user,
                    action='update',
                    object_type='report',
                    object_id=report.id,
                    details=f'Updated report status to {serializer.validated_data.get("status")}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'Report updated successfully',
                    'report': ReportSerializer(report).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating report: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SystemMaintenanceCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create system maintenance with custom validation"""
        serializer = SystemMaintenanceCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # Check for overlapping maintenance windows
                scheduled_start = serializer.validated_data.get('scheduled_start')
                scheduled_end = serializer.validated_data.get('scheduled_end')
                
                overlapping_maintenance = SystemMaintenance.objects.filter(
                    status__in=['scheduled', 'in_progress'],
                    scheduled_start__lt=scheduled_end,
                    scheduled_end__gt=scheduled_start
                ).exists()
                
                if overlapping_maintenance:
                    return Response({
                        'error': 'Maintenance window overlaps with existing scheduled maintenance'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create maintenance
                maintenance = serializer.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user,
                    action='create',
                    object_type='system_maintenance',
                    object_id=maintenance.id,
                    details=f'Scheduled maintenance: {maintenance.maintenance_type}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'System maintenance scheduled successfully',
                    'maintenance': SystemMaintenanceSerializer(maintenance).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error scheduling maintenance: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SystemMaintenanceUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        """Get maintenance and check access"""
        try:
            return SystemMaintenance.objects.get(id=pk)
        except SystemMaintenance.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Update maintenance with custom logic"""
        maintenance = self.get_object(pk)
        if not maintenance:
            return Response({'error': 'Maintenance not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SystemMaintenanceUpdateSerializer(maintenance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Update maintenance
                serializer.save()
                
                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    admin=request.user,
                    action='update',
                    object_type='system_maintenance',
                    object_id=maintenance.id,
                    details=f'Updated maintenance status to {serializer.validated_data.get("status")}',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return Response({
                    'message': 'Maintenance updated successfully',
                    'maintenance': SystemMaintenanceSerializer(maintenance).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating maintenance: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom API endpoints
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def dashboard_statistics(request):
    """Get comprehensive dashboard statistics"""
    try:
        # Parse date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Base queryset with date filtering
        base_filter = {}
        if date_from:
            base_filter['created_at__date__gte'] = date_from
        if date_to:
            base_filter['created_at__date__lte'] = date_to
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users = User.objects.filter(**base_filter).count()
        
        # Order statistics
        from Orders.models import Order
        total_orders = Order.objects.count()
        completed_orders = Order.objects.filter(status='delivered').count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Revenue statistics
        total_revenue = Order.objects.filter(
            payment_status='paid',
            **base_filter
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Dispute statistics
        total_disputes = Dispute.objects.count()
        resolved_disputes = Dispute.objects.filter(status='resolved').count()
        pending_disputes = Dispute.objects.filter(status='pending').count()
        
        # Report statistics
        total_reports = Report.objects.count()
        resolved_reports = Report.objects.filter(status='resolved').count()
        pending_reports = Report.objects.filter(status='pending').count()
        
        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'new': new_users
            },
            'orders': {
                'total': total_orders,
                'completed': completed_orders,
                'pending': pending_orders
            },
            'revenue': {
                'total': total_revenue,
                'period': f"{date_from or 'All time'} - {date_to or 'Now'}"
            },
            'disputes': {
                'total': total_disputes,
                'resolved': resolved_disputes,
                'pending': pending_disputes
            },
            'reports': {
                'total': total_reports,
                'resolved': resolved_reports,
                'pending': pending_reports
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def user_management(request):
    """Bulk user management actions"""
    serializer = UserManagementSerializer(data=request.data)
    if serializer.is_valid():
        try:
            action = serializer.validated_data['action']
            user_ids = serializer.validated_data['user_ids']
            reason = serializer.validated_data.get('reason', '')
            
            users = User.objects.filter(id__in=user_ids)
            affected_count = 0
            
            for user in users:
                try:
                    if action == 'activate':
                        user.is_active = True
                        user.save()
                    elif action == 'deactivate':
                        user.is_active = False
                        user.save()
                    elif action == 'suspend':
                        user.is_active = False
                        # Add suspension logic here
                        user.save()
                    
                    affected_count += 1
                    
                    # Log the action
                    AuditLog.objects.create(
                        user=user,
                        admin=request.user,
                        action=action,
                        object_type='user',
                        object_id=user.id,
                        details=f'User {action}ed. Reason: {reason}',
                        ip_address=request.META.get('REMOTE_ADDR', '')
                    )
                    
                except Exception as e:
                    continue
            
            return Response({
                'message': f'{action} action completed successfully',
                'affected_users': affected_count,
                'total_users': len(user_ids)
            })
            
        except Exception as e:
            return Response({
                'error': f'Error performing user management action: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def content_moderation(request):
    """Content moderation actions"""
    serializer = ContentModerationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            action = serializer.validated_data['action']
            content_type = serializer.validated_data['content_type']
            content_id = serializer.validated_data['content_id']
            reason = serializer.validated_data.get('reason', '')
            admin_notes = serializer.validated_data.get('admin_notes', '')
            
            # Get content object based on type
            content_object = None
            if content_type == 'product':
                from Products.models import Product
                content_object = Product.objects.get(id=content_id)
            elif content_type == 'user':
                content_object = User.objects.get(id=content_id)
            elif content_type == 'order':
                from Orders.models import Order
                content_object = Order.objects.get(id=content_id)
            
            if not content_object:
                return Response({
                    'error': 'Content object not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Perform moderation action
            if action == 'approve':
                if hasattr(content_object, 'status'):
                    content_object.status = 'approved'
                    content_object.save()
            elif action == 'reject':
                if hasattr(content_object, 'status'):
                    content_object.status = 'rejected'
                    content_object.save()
            elif action == 'remove':
                if hasattr(content_object, 'is_active'):
                    content_object.is_active = False
                    content_object.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                admin=request.user,
                action=action,
                object_type=content_type,
                object_id=content_id,
                details=f'Content {action}ed. Reason: {reason}. Notes: {admin_notes}',
                ip_address=request.META.get('REMOTE_ADDR', '')
            )
            
            return Response({
                'message': f'Content {action}ed successfully',
                'content_type': content_type,
                'content_id': content_id
            })
            
        except Exception as e:
            return Response({
                'error': f'Error performing content moderation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
