from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

from .views import UserList, UserDetail

urlpatterns = [
    path('/', UserList.as_view(), name='user-list'),
    path('/<int:pk>/', UserDetail.as_view(), name='user-detail')
]
