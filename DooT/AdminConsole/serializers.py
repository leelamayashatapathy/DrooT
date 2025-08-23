from rest_framework import serializers
from .models import AdminProfile, SystemSettings, AuditLog, Dispute, DisputeMessage, Report, SystemMaintenance

class AdminProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AdminProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class AdminProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ['role', 'department', 'permissions', 'phone', 'profile_image']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class SystemSettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ['value', 'description', 'is_active']

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp', 'ip_address']

class DisputeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Dispute
        fields = '__all__'
        read_only_fields = ['id', 'dispute_id', 'created_at', 'updated_at']

class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['order', 'dispute_type', 'description', 'evidence_files']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DisputeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['status', 'admin_notes', 'resolution', 'resolved_at']

class DisputeMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    
    class Meta:
        model = DisputeMessage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class DisputeMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeMessage
        fields = ['dispute', 'message', 'is_admin_message']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if validated_data.get('is_admin_message', False):
            validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)

class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.name', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'report_id', 'created_at', 'updated_at']

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'report_type', 'description', 'evidence_files']
    
    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)

class ReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['status', 'admin_notes', 'resolution', 'resolved_at']

class SystemMaintenanceSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    
    class Meta:
        model = SystemMaintenance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class SystemMaintenanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMaintenance
        fields = ['maintenance_type', 'description', 'scheduled_start', 'scheduled_end', 'affected_services']
    
    def create(self, validated_data):
        validated_data['admin'] = self.context['request'].user
        return super().create(validated_data)

class SystemMaintenanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMaintenance
        fields = ['status', 'actual_start', 'actual_end', 'notes', 'completion_notes']

class DashboardStatisticsSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    include_charts = serializers.BooleanField(default=True)

class UserManagementSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'suspend', 'delete'])
    user_ids = serializers.ListField(child=serializers.IntegerField())
    reason = serializers.CharField(required=False)
    
    def validate_action(self, value):
        if value == 'delete':
            raise serializers.ValidationError("Delete action is not allowed for safety reasons")
        return value

class ContentModerationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'flag', 'remove'])
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    reason = serializers.CharField(required=False)
    admin_notes = serializers.CharField(required=False)
