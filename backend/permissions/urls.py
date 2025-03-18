from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

from .views import PermissionList, PermissionDetail

urlpatterns = [
    path('/', PermissionList.as_view(), name='permission-list'),
    path('/<int:pk>/', PermissionDetail.as_view(), name='permission-detail')
]
