from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import F
from .models import Product, ProductImage, Subscription, Usage, FileUpload, APIKey, Notification, ActivityLog, Organization, User, Category
from .serializers import ProductSerializer, ProductImageSerializer, SubscriptionSerializer, UsageSerializer, FileUploadSerializer, APIKeySerializer, NotificationSerializer, ActivityLogSerializer, OrganizationSerializer, UserSerializer, CategorySerializer
from .filters import ProductFilter, FileUploadFilter, NotificationFilter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password

filterset_fields = ['is_active']
search_fields = ['name', 'slug']
class BaseOrgViewSet(viewsets.ModelViewSet):
	"""Stub for base viewset, replace with your actual implementation."""
	pass



class ProductViewSet(BaseOrgViewSet):
	queryset = Product.objects.select_related('organization', 'category').prefetch_related('images').all()
	serializer_class = ProductSerializer
	filterset_class = ProductFilter
	search_fields = ['product_name', 'description']

	@action(detail=True, methods=['post'])
	def increment_view(self, request, pk=None):
		Product.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
		return Response({"ok": True})



class ProductImageViewSet(BaseOrgViewSet):
	queryset = ProductImage.objects.select_related('product', 'product__organization').all()
	serializer_class = ProductImageSerializer



class SubscriptionViewSet(BaseOrgViewSet):
	queryset = Subscription.objects.select_related('organization').all()
	serializer_class = SubscriptionSerializer



class UsageViewSet(BaseOrgViewSet):
	queryset = Usage.objects.select_related('organization').all()
	serializer_class = UsageSerializer



class FileUploadViewSet(BaseOrgViewSet):
	queryset = FileUpload.objects.select_related('organization', 'uploaded_by').all()
	serializer_class = FileUploadSerializer
	parser_classes = [MultiPartParser, FormParser]
	filterset_class = FileUploadFilter

	def perform_create(self, serializer):
		serializer.save(
			organization=getattr(self.request, 'organization', None),
			uploaded_by=self.request.user
		)



class APIKeyViewSet(BaseOrgViewSet):
	queryset = APIKey.objects.select_related('organization', 'created_by').all()
	serializer_class = APIKeySerializer



class NotificationViewSet(BaseOrgViewSet):
	queryset = Notification.objects.select_related('organization', 'user').all()
	serializer_class = NotificationSerializer
	filterset_class = NotificationFilter

	@action(detail=True, methods=['post'])
	def mark_read(self, request, pk=None):
		obj = self.get_object()
		obj.mark_as_read()
		return Response(NotificationSerializer(obj).data)



class ActivityLogViewSet(BaseOrgViewSet):
	queryset = ActivityLog.objects.select_related('organization', 'user').all()
	serializer_class = ActivityLogSerializer
	http_method_names = ['get', 'head', 'options', 'delete'] # read-only + delete


class OrganizationViewSet(viewsets.ModelViewSet):
	queryset = Organization.objects.all()
	serializer_class = OrganizationSerializer


class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from .serializers import UserSerializer
        return Response(UserSerializer(user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'detail': 'New password required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'})


class ToggleTwoFactorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Dummy implementation for 2FA toggle
        user = request.user
        enable = request.data.get('enable')
        # Here you would implement actual 2FA logic
        if enable:
            # Enable 2FA for user
            return Response({'detail': '2FA enabled.'}, status=status.HTTP_200_OK)
        else:
            # Disable 2FA for user
            return Response({'detail': '2FA disabled.'}, status=status.HTTP_200_OK)