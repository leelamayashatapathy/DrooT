from rest_framework import serializers
from Users.serializers import SellerProfileSerializer

class SellerDashboardSerializer(serializers.Serializer):
    profile = SellerProfileSerializer()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_orders = serializers.IntegerField()

class SellerAnalyticsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_revenue = serializers.ListField(child=serializers.DictField())
    top_products = serializers.ListField(child=serializers.DictField())
    order_status_distribution = serializers.DictField()
