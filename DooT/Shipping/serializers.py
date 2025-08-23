from rest_framework import serializers
from .models import ShippingZone, ShippingMethod, ShippingRate, Shipment, ShipmentTracking, Address

class ShippingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingZone
        fields = '__all__'

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'

class ShippingRateSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='shipping_zone.name', read_only=True)
    method_name = serializers.CharField(source='shipping_method.name', read_only=True)
    
    class Meta:
        model = ShippingRate
        fields = '__all__'

class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class ShipmentSerializer(serializers.ModelSerializer):
    tracking_events = ShipmentTrackingSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)
    
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['id', 'shipment_id', 'order', 'created_at', 'updated_at']

class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['order', 'shipping_method', 'shipping_rate', 'shipping_cost', 
                 'package_weight', 'package_dimensions', 'origin_address', 
                 'destination_address', 'tracking_number', 'carrier']

class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['status', 'tracking_number', 'carrier', 'tracking_url', 
                 'estimated_delivery', 'notes', 'admin_notes']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_type', 'first_name', 'last_name', 'company', 
                 'address_line1', 'address_line2', 'city', 'state', 
                 'country', 'zip_code', 'phone', 'is_default']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ShippingCalculatorSerializer(serializers.Serializer):
    origin_country = serializers.CharField()
    origin_state = serializers.CharField(required=False)
    origin_city = serializers.CharField(required=False)
    origin_zip = serializers.CharField(required=False)
    
    destination_country = serializers.CharField()
    destination_state = serializers.CharField(required=False)
    destination_city = serializers.CharField(required=False)
    destination_zip = serializers.CharField(required=False)
    
    package_weight = serializers.DecimalField(max_digits=8, decimal_places=2)
    item_count = serializers.IntegerField()
    order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, attrs):
        if attrs['package_weight'] <= 0:
            raise serializers.ValidationError("Package weight must be greater than 0")
        if attrs['item_count'] <= 0:
            raise serializers.ValidationError("Item count must be greater than 0")
        if attrs['order_value'] <= 0:
            raise serializers.ValidationError("Order value must be greater than 0")
        return attrs
