

from rest_framework import serializers
from .models import ProductImage, Product, Subscription, Usage, FileUpload, APIKey, Notification, ActivityLog

class ProductImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductImage
    fields = '__all__'
    read_only_fields = ('id', 'created_at')

class ProductSerializer(serializers.ModelSerializer):
  images = ProductImageSerializer(many=True, read_only=True)
  effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  is_in_stock = serializers.BooleanField(read_only=True)
  profit_margin = serializers.SerializerMethodField()

  def get_profit_margin(self, obj):
    return float(obj.profit_margin) if obj.profit_margin is not None else 0

  class Meta:
    model = Product
    fields = '__all__'
    read_only_fields = (
      'id', 'organization', 'created_at', 'updated_at', 'created_by', 'updated_by',
      'view_count', 'rating', 'review_count', 'sku', 'effective_price', 'is_in_stock'
    )

class SubscriptionSerializer(serializers.ModelSerializer):
  is_active = serializers.BooleanField(read_only=True)

  class Meta:
    model = Subscription
    fields = '__all__'
    read_only_fields = ('id', 'created_at', 'updated_at')

class UsageSerializer(serializers.ModelSerializer):
  usage_percentage = serializers.FloatField(read_only=True)
  is_limit_exceeded = serializers.BooleanField(read_only=True)

  class Meta:
    model = Usage
    fields = '__all__'
    read_only_fields = ('id', 'created_at', 'updated_at')


class FileUploadSerializer(serializers.ModelSerializer):
  file_size_formatted = serializers.CharField(read_only=True)

  class Meta:
    model = FileUpload
    fields = '__all__'
    read_only_fields = ('id', 'uploaded_by', 'organization', 'file_size', 'download_count', 'created_at', 'updated_at')



class APIKeySerializer(serializers.ModelSerializer):
  is_expired = serializers.BooleanField(read_only=True)

  class Meta:
    model = APIKey
    fields = '__all__'
fields = '__all__'
read_only_fields = ('id', 'key', 'key_preview', 'usage_count', 'last_used', 'created_at', 'updated_at')



class NotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Notification
    fields = '__all__'
    read_only_fields = ('id', 'created_at', 'read_at', 'organization')



class ActivityLogSerializer(serializers.ModelSerializer):
  class Meta:
    model = ActivityLog
    fields = '__all__'
    read_only_fields = ('id', 'created_at')