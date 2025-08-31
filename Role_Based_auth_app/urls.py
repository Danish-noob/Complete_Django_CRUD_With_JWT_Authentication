from django.urls import path
from .views import ProductListView , AdminOnlyUserCreateView , AdminProductView 
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
# from .views import CreateUserView



urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user/', AdminOnlyUserCreateView.as_view(), name='create-user'),
    path('add/products/', AdminProductView.as_view(), name='admin_add_product'),
    path('delete/products/<int:product_id>/', AdminProductView.as_view(), name='admin_delete_product'),
    
]
