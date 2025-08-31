from django_filters import rest_framework as filters
from .models import Product, FileUpload, Notification



class ProductFilter(filters.FilterSet):
	min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
	max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
	category = filters.CharFilter(field_name='category__slug')
	q = filters.CharFilter(method='search')

	class Meta:
		model = Product
		fields = ['is_active', 'is_featured', 'is_digital']

	def search(self, queryset, name, value):
		return queryset.filter(product_name__icontains=value) | queryset.filter(description__icontains=value)



class FileUploadFilter(filters.FilterSet):
	q = filters.CharFilter(method='search')

	class Meta:
		model = FileUpload
		fields = ['is_public', 'file_type']

	def search(self, queryset, name, value):
		return queryset.filter(original_name__icontains=value)



class NotificationFilter(filters.FilterSet):
	class Meta:
		model = Notification
		fields = ['is_read', 'notification_type']