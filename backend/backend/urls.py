
from django.contrib import admin
from django.urls import path ,include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/companies',include('companies.urls')) ,
    path('api/users', include('users.urls')),
    path('api/roles', include('roles.urls')),
    path('api/permissions', include('permissions.urls')),
    path('api/resumes', include('resumes.urls')),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   
]
