from django.urls import path

from .views import PermissionList, PermissionDetail

urlpatterns = [
    path('', PermissionList.as_view(), name='permission-list'),
    path('/<int:pk>', PermissionDetail.as_view(), name='permission-detail')
]
