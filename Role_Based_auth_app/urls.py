from django.urls import path
from .views import (ProductListView, AdminOnlyUserCreateView, AdminProductView, 
                   MyTokenObtainPairView, MeView, ChangePasswordView, ToggleTwoFactorView)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Product endpoints
    path('products/', ProductListView.as_view(), name='products'),
    path('add/products/', AdminProductView.as_view(), name='admin_add_product'),
    path('delete/products/<uuid:product_id>/', AdminProductView.as_view(), name='admin_delete_product'),
    
    # Authentication endpoints
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('create-user/', AdminOnlyUserCreateView.as_view(), name='create-user'),
    path('me/', MeView.as_view(), name='me'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('me/2fa/', ToggleTwoFactorView.as_view(), name='toggle_2fa'),
]
