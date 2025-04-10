from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

from .views import RoleList, RoleDetail

urlpatterns = [
    path('', RoleList.as_view(), name='role-list'),
    path('/<int:pk>', RoleDetail.as_view(), name='role-detail')
]
