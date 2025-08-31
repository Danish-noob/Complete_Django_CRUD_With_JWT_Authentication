from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import (
TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from Role_Based_auth_app import views as app_views


router = routers.DefaultRouter()
router.register(r'organizations', app_views.OrganizationViewSet, basename='organization')
router.register(r'users', app_views.UserViewSet, basename='user')
router.register(r'categories', app_views.CategoryViewSet, basename='category')
router.register(r'products', app_views.ProductViewSet, basename='product')
router.register(r'product-images', app_views.ProductImageViewSet, basename='productimage')
router.register(r'subscription', app_views.SubscriptionViewSet, basename='subscription')
router.register(r'usage', app_views.UsageViewSet, basename='usage')
router.register(r'files', app_views.FileUploadViewSet, basename='fileupload')
router.register(r'api-keys', app_views.APIKeyViewSet, basename='apikey')
router.register(r'notifications', app_views.NotificationViewSet, basename='notification')
router.register(r'activity', app_views.ActivityLogViewSet, basename='activity')


urlpatterns = [
path('admin/', admin.site.urls),


# Auth (JWT)
path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),


# Me endpoints
path('api/me/', app_views.MeView.as_view(), name='me'),
path('api/me/change-password/', app_views.ChangePasswordView.as_view(), name='change_password'),
path('api/me/2fa/', app_views.ToggleTwoFactorView.as_view(), name='toggle_2fa'),


# API schema + docs
path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),


# API v1 router
path('api/', include(router.urls)),
]


if settings.DEBUG:
	from django.conf.urls.static import static
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)