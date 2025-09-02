from rest_framework import viewsets, permissions, mixins, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import F
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import (Product, ProductImage, Subscription, Usage, FileUpload, 
                     APIKey, Notification, ActivityLog, Organization, User, Category)
from .serializers import (ProductSerializer, ProductImageSerializer, SubscriptionSerializer, 
                         UsageSerializer, FileUploadSerializer, APIKeySerializer, 
                         NotificationSerializer, ActivityLogSerializer, OrganizationSerializer, 
                         UserSerializer, CategorySerializer, MyTokenObtainPairSerializer)
from .filters import ProductFilter, FileUploadFilter, NotificationFilter
from .permissions import (IsOwner, IsAdminOrOwner, IsManagerOrAbove, IsSameOrganization,
                         CanCreateUsers, CanManageProducts, CanDeleteProducts)

User = get_user_model()


class BaseOrgViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that filters by organization and applies organization-level permissions
    """
    permission_classes = [IsAuthenticated, IsSameOrganization]
    
    def get_queryset(self):
        """Filter queryset by user's organization"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            if hasattr(queryset.model, 'organization'):
                return queryset.filter(organization=self.request.user.organization)
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign organization and user when creating objects"""
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            if 'organization' in serializer.validated_data or hasattr(serializer.Meta.model, 'organization'):
                serializer.save(organization=self.request.user.organization)
        
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)


class ProductViewSet(BaseOrgViewSet):
    queryset = Product.objects.select_related('organization', 'category').prefetch_related('images').all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['product_name', 'name', 'description']
    permission_classes = [IsAuthenticated, CanManageProducts, IsSameOrganization]

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        Product.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        return Response({"ok": True})


class ProductImageViewSet(BaseOrgViewSet):
    queryset = ProductImage.objects.select_related('product', 'product__organization').all()
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]


class SubscriptionViewSet(BaseOrgViewSet):
    queryset = Subscription.objects.select_related('organization').all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]


class UsageViewSet(BaseOrgViewSet):
    queryset = Usage.objects.select_related('organization').all()
    serializer_class = UsageSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]


class FileUploadViewSet(BaseOrgViewSet):
    queryset = FileUpload.objects.select_related('organization', 'uploaded_by').all()
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_class = FileUploadFilter

    def perform_create(self, serializer):
        serializer.save(
            organization=getattr(self.request.user, 'organization', None),
            uploaded_by=self.request.user
        )


class APIKeyViewSet(BaseOrgViewSet):
    queryset = APIKey.objects.select_related('organization', 'created_by').all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]


class NotificationViewSet(BaseOrgViewSet):
    queryset = Notification.objects.select_related('organization', 'user').all()
    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter

    def get_queryset(self):
        """Filter notifications for the current user"""
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        obj = self.get_object()
        obj.mark_as_read()
        return Response(NotificationSerializer(obj).data)


class ActivityLogViewSet(BaseOrgViewSet):
    queryset = ActivityLog.objects.select_related('organization', 'user').all()
    serializer_class = ActivityLogSerializer
    http_method_names = ['get', 'head', 'options', 'delete']  # read-only + delete
    permission_classes = [IsAuthenticated, IsAdminOrOwner]


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own organization"""
        if self.request.user.is_staff:
            return Organization.objects.all()
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            return Organization.objects.filter(id=self.request.user.organization.id)
        return Organization.objects.none()


class UserViewSet(BaseOrgViewSet):
    queryset = User.objects.select_related('organization').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, CanCreateUsers]
    
    def get_queryset(self):
        """Filter users by organization"""
        if self.request.user.is_staff:
            return User.objects.all()
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            return User.objects.filter(organization=self.request.user.organization)
        return User.objects.none()


class CategoryViewSet(BaseOrgViewSet):
    queryset = Category.objects.select_related('organization').all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]


# Custom JWT Token View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# User Management Views
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')
        
        if not new_password:
            return Response({'detail': 'New password required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not old_password:
            return Response({'detail': 'Old password required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify old password
        if not user.check_password(old_password):
            return Response({'detail': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        enable = request.data.get('enable', False)
        
        user.two_factor_enabled = enable
        user.save()
        
        if enable:
            return Response({'detail': '2FA enabled.', 'two_factor_enabled': True}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '2FA disabled.', 'two_factor_enabled': False}, status=status.HTTP_200_OK)


# Product Management Views (for backward compatibility with existing URLs)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    search_fields = ['product_name', 'name', 'description']
    
    def get_queryset(self):
        queryset = Product.objects.select_related('organization', 'category').prefetch_related('images')
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            return queryset.filter(organization=self.request.user.organization)
        return queryset.none()


class AdminOnlyUserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, CanCreateUsers]
    
    def perform_create(self, serializer):
        # Auto-assign organization from the requesting user
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            serializer.save(organization=self.request.user.organization)


class AdminProductView(APIView):
    permission_classes = [IsAuthenticated, CanManageProducts]
    
    def post(self, request):
        """Create a new product"""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-assign organization and creator
            serializer.save(
                organization=getattr(request.user, 'organization', None),
                created_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, product_id):
        """Delete a product"""
        try:
            product = Product.objects.get(
                id=product_id,
                organization=getattr(request.user, 'organization', None)
            )
            
            # Check if user has delete permissions
            if not request.user.role in ['admin', 'owner']:
                return Response(
                    {'detail': 'You do not have permission to delete products.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            product.delete()
            return Response({'detail': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
