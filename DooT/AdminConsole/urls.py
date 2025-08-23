from django.urls import path
from . import views

app_name = 'admin_console'

urlpatterns = [
    # Admin Profiles
    path('profiles/', views.AdminProfileListView.as_view(), name='admin-profile-list'),
    path('profiles/create/', views.AdminProfileCreateView.as_view(), name='admin-profile-create'),
    path('profiles/<int:pk>/', views.AdminProfileDetailView.as_view(), name='admin-profile-detail'),
    
    # System Settings
    path('settings/', views.SystemSettingsListView.as_view(), name='system-settings-list'),
    path('settings/<int:pk>/', views.SystemSettingsDetailView.as_view(), name='system-settings-detail'),
    path('settings/<int:pk>/update/', views.SystemSettingsUpdateView.as_view(), name='system-settings-update'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    
    # Disputes
    path('disputes/', views.DisputeListView.as_view(), name='dispute-list'),
    path('disputes/create/', views.DisputeCreateView.as_view(), name='dispute-create'),
    path('disputes/<int:pk>/', views.DisputeDetailView.as_view(), name='dispute-detail'),
    path('disputes/<int:pk>/update/', views.DisputeUpdateView.as_view(), name='dispute-update'),
    path('disputes/<int:dispute_id>/messages/', views.DisputeMessageListView.as_view(), name='dispute-message-list'),
    path('disputes/messages/create/', views.DisputeMessageCreateView.as_view(), name='dispute-message-create'),
    
    # Reports
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/update/', views.ReportUpdateView.as_view(), name='report-update'),
    
    # System Maintenance
    path('maintenance/', views.SystemMaintenanceListView.as_view(), name='maintenance-list'),
    path('maintenance/create/', views.SystemMaintenanceCreateView.as_view(), name='maintenance-create'),
    path('maintenance/<int:pk>/', views.SystemMaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenance/<int:pk>/update/', views.SystemMaintenanceUpdateView.as_view(), name='maintenance-update'),
    
    # Dashboard and Management
    path('dashboard/statistics/', views.dashboard_statistics, name='dashboard-statistics'),
    path('user-management/', views.user_management, name='user-management'),
    path('content-moderation/', views.content_moderation, name='content-moderation'),
]
