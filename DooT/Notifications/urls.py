from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification Templates (Admin)
    path('templates/', views.NotificationTemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='template-detail'),
    
    # User Notifications
    path('', views.UserNotificationListView.as_view(), name='user-notification-list'),
    path('<int:pk>/', views.UserNotificationDetailView.as_view(), name='user-notification-detail'),
    path('<int:pk>/update/', views.UserNotificationUpdateView.as_view(), name='user-notification-update'),
    
    # Notification Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
    
    # Notification Actions
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark-read'),
    path('count/', views.notification_count, name='notification-count'),
    
    # Admin Functions
    path('admin/create/', views.NotificationCreateView.as_view(), name='create'),
    path('admin/bulk/', views.BulkNotificationView.as_view(), name='bulk-create'),
    path('admin/statistics/', views.notification_statistics, name='statistics'),
    
    # Delivery Logs (Admin)
    path('admin/email-logs/', views.EmailLogListView.as_view(), name='email-logs'),
    path('admin/sms-logs/', views.SMSLogListView.as_view(), name='sms-logs'),
]
