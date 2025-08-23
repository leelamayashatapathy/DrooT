from rest_framework import serializers
from .models import NotificationTemplate, Notification, UserNotification, EmailLog, SMSLog, NotificationPreference

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.notification_type', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['template', 'recipient', 'related_object_type', 'related_object_id', 'context_data', 'scheduled_at']
    
    def create(self, validated_data):
        # Get template
        template = validated_data['template']
        
        # Create notification
        notification = Notification.objects.create(
            template=template,
            recipient=validated_data['recipient'],
            related_object_type=validated_data.get('related_object_type'),
            related_object_id=validated_data.get('related_object_id'),
            context_data=validated_data.get('context_data', {}),
            scheduled_at=validated_data.get('scheduled_at')
        )
        
        # Create user notification
        UserNotification.objects.create(
            user=validated_data['recipient'],
            notification=notification,
            is_read=False
        )
        
        return notification

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    notification_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserNotification
        fields = ['id', 'notification', 'notification_id', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserNotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['is_read']

class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ['id', 'sent_at', 'created_at']

class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = '__all__'
        read_only_fields = ['id', 'sent_at', 'created_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled', 'frequency']

class BulkNotificationSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    user_ids = serializers.ListField(child=serializers.IntegerField())
    context_data = serializers.JSONField(required=False)
    scheduled_at = serializers.DateTimeField(required=False)
    
    def validate_template_id(self, value):
        try:
            NotificationTemplate.objects.get(id=value)
        except NotificationTemplate.DoesNotExist:
            raise serializers.ValidationError("Invalid notification template")
        return value

class NotificationFilterSerializer(serializers.Serializer):
    notification_type = serializers.CharField(required=False)
    is_read = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
