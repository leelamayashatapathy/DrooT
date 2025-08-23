from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import NotificationTemplate, Notification, UserNotification, EmailLog, SMSLog, NotificationPreference
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer, NotificationCreateSerializer,
    UserNotificationSerializer, UserNotificationUpdateSerializer, EmailLogSerializer,
    SMSLogSerializer, NotificationPreferenceSerializer, NotificationPreferenceUpdateSerializer,
    BulkNotificationSerializer, NotificationFilterSerializer
)

# Keep generics for simple listing and retrieval
class NotificationTemplateListView(generics.ListAPIView):
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]

class NotificationTemplateDetailView(generics.RetrieveAPIView):
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]

class EmailLogListView(generics.ListAPIView):
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'recipient']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-sent_at']

class SMSLogListView(generics.ListAPIView):
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'recipient']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-sent_at']

# Convert to APIView for custom operations
class UserNotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user notifications with custom filtering and pagination"""
        try:
            # Get filter parameters
            notification_type = request.query_params.get('notification_type')
            is_read = request.query_params.get('is_read')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Build queryset
            queryset = UserNotification.objects.filter(user=request.user)
            
            # Apply filters
            if notification_type:
                queryset = queryset.filter(notification__template__notification_type=notification_type)
            
            if is_read is not None:
                queryset = queryset.filter(is_read=is_read.lower() == 'true')
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            # Order by creation date (newest first)
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            total_count = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            
            notifications = queryset[start:end]
            
            serializer = UserNotificationSerializer(notifications, many=True)
            
            return Response({
                'notifications': serializer.data,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'unread_count': UserNotification.objects.filter(user=request.user, is_read=False).count()
            })
            
        except Exception as e:
            return Response({
                'error': f'Error retrieving notifications: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserNotificationDetailView(generics.RetrieveAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user)

class UserNotificationUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        """Get notification and check ownership"""
        try:
            return UserNotification.objects.get(id=pk, user=self.request.user)
        except UserNotification.DoesNotExist:
            return None
    
    def put(self, request, pk):
        """Mark notification as read/unread"""
        notification = self.get_object(pk)
        if not notification:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserNotificationUpdateSerializer(notification, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Update read status
                is_read = serializer.validated_data.get('is_read')
                if is_read and not notification.is_read:
                    notification.read_at = timezone.now()
                elif not is_read:
                    notification.read_at = None
                
                serializer.save()
                
                return Response({
                    'message': 'Notification updated successfully',
                    'notification': UserNotificationSerializer(notification).data
                })
                
            except Exception as e:
                return Response({
                    'error': f'Error updating notification: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Create notification with custom logic"""
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create notification
                notification = serializer.save()
                
                # Send notification based on template type
                self._send_notification(notification)
                
                return Response({
                    'message': 'Notification created and sent successfully',
                    'notification': NotificationSerializer(notification).data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error creating notification: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_notification(self, notification):
        """Send notification based on template type and user preferences"""
        template = notification.template
        user = notification.recipient
        
        # Get user preferences
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        
        # Send email notification
        if template.email_enabled and preferences.email_enabled:
            self._send_email_notification(notification)
        
        # Send SMS notification
        if template.sms_enabled and preferences.sms_enabled:
            self._send_sms_notification(notification)
        
        # Send push notification (placeholder for future implementation)
        if template.push_enabled and preferences.push_enabled:
            self._send_push_notification(notification)
    
    def _send_email_notification(self, notification):
        """Send email notification and log it"""
        try:
            template = notification.template
            user = notification.recipient
            
            # Render email content
            subject = self._render_template(template.email_subject, notification.context_data)
            body = self._render_template(template.email_body, notification.context_data)
            
            # In a real application, send email here
            # For now, just log it
            EmailLog.objects.create(
                notification=notification,
                recipient=user.email,
                subject=subject,
                body=body,
                status='sent',
                sent_at=timezone.now()
            )
            
        except Exception as e:
            # Log failure
            EmailLog.objects.create(
                notification=notification,
                recipient=user.email,
                subject='',
                body='',
                status='failed',
                error_message=str(e),
                sent_at=timezone.now()
            )
    
    def _send_sms_notification(self, notification):
        """Send SMS notification and log it"""
        try:
            template = notification.template
            user = notification.recipient
            
            # Render SMS content
            message = self._render_template(template.sms_body, notification.context_data)
            
            # In a real application, send SMS here
            # For now, just log it
            SMSLog.objects.create(
                notification=notification,
                recipient=user.phone,
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            
        except Exception as e:
            # Log failure
            SMSLog.objects.create(
                notification=notification,
                recipient=user.phone,
                message='',
                status='failed',
                error_message=str(e),
                sent_at=timezone.now()
            )
    
    def _send_push_notification(self, notification):
        """Send push notification (placeholder)"""
        # This would integrate with Firebase, OneSignal, or similar service
        pass
    
    def _render_template(self, template_text, context_data):
        """Simple template rendering (in production, use a proper template engine)"""
        if not template_text:
            return ''
        
        # Replace placeholders with context data
        rendered = template_text
        for key, value in context_data.items():
            placeholder = f'{{{{{key}}}}}'
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered

class BulkNotificationView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Send bulk notifications to multiple users"""
        serializer = BulkNotificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                template_id = serializer.validated_data['template_id']
                user_ids = serializer.validated_data['user_ids']
                context_data = serializer.validated_data.get('context_data', {})
                scheduled_at = serializer.validated_data.get('scheduled_at')
                
                # Get template
                template = NotificationTemplate.objects.get(id=template_id)
                
                # Get users
                from Users.models import User
                users = User.objects.filter(id__in=user_ids, is_active=True)
                
                notifications_created = 0
                notifications_failed = 0
                
                for user in users:
                    try:
                        # Create notification
                        notification = Notification.objects.create(
                            template=template,
                            recipient=user,
                            context_data=context_data,
                            scheduled_at=scheduled_at
                        )
                        
                        # Create user notification
                        UserNotification.objects.create(
                            user=user,
                            notification=notification,
                            is_read=False
                        )
                        
                        notifications_created += 1
                        
                    except Exception as e:
                        notifications_failed += 1
                        continue
                
                return Response({
                    'message': f'Bulk notification created successfully',
                    'notifications_created': notifications_created,
                    'notifications_failed': notifications_failed,
                    'total_users': len(users)
                }, status=status.HTTP_201_CREATED)
                
            except NotificationTemplate.DoesNotExist:
                return Response({
                    'error': 'Notification template not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': f'Error creating bulk notifications: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationPreferenceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user notification preferences"""
        try:
            preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
            serializer = NotificationPreferenceSerializer(preferences)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'error': f'Error retrieving preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update user notification preferences"""
        try:
            preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
            serializer = NotificationPreferenceUpdateSerializer(preferences, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    'message': 'Notification preferences updated successfully',
                    'preferences': NotificationPreferenceSerializer(preferences).data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error updating preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Custom API endpoints
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all user notifications as read"""
    try:
        unread_notifications = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        count = unread_notifications.count()
        unread_notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': f'{count} notifications marked as read'
        })
        
    except Exception as e:
        return Response({
            'error': f'Error marking notifications as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark specific notification as read"""
    try:
        notification = UserNotification.objects.get(
            id=notification_id,
            user=request.user
        )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'message': 'Notification marked as read'
        })
        
    except UserNotification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error marking notification as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_count(request):
    """Get unread notification count"""
    try:
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'unread_count': unread_count
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving notification count: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def notification_statistics(request):
    """Get notification statistics for admin dashboard"""
    try:
        total_notifications = Notification.objects.count()
        total_user_notifications = UserNotification.objects.count()
        unread_notifications = UserNotification.objects.filter(is_read=False).count()
        
        # Email delivery statistics
        email_sent = EmailLog.objects.filter(status='sent').count()
        email_failed = EmailLog.objects.filter(status='failed').count()
        email_success_rate = (email_sent / (email_sent + email_failed)) * 100 if (email_sent + email_failed) > 0 else 0
        
        # SMS delivery statistics
        sms_sent = SMSLog.objects.filter(status='sent').count()
        sms_failed = SMSLog.objects.filter(status='failed').count()
        sms_success_rate = (sms_sent / (sms_sent + sms_failed)) * 100 if (sms_sent + sms_failed) > 0 else 0
        
        return Response({
            'total_notifications': total_notifications,
            'total_user_notifications': total_user_notifications,
            'unread_notifications': unread_notifications,
            'email_delivery': {
                'sent': email_sent,
                'failed': email_failed,
                'success_rate': round(email_success_rate, 2)
            },
            'sms_delivery': {
                'sent': sms_sent,
                'failed': sms_failed,
                'success_rate': round(sms_success_rate, 2)
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
