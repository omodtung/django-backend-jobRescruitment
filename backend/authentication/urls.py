# myapp/urls.py

from django.urls import path
from .views import CustomTokenObtainPairView
from .views import CustomTokenRefreshView
from .views import AccountApiView
from .views import RegistertApiView

urlpatterns = [
    path('/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('/account', AccountApiView.as_view(), name='account'),
    path('/register', RegistertApiView.as_view(), name='register')
]
