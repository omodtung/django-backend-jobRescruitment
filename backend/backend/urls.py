
from django.contrib import admin
from django.urls import path ,include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', include('users.urls')),
    path('api/roles', include('roles.urls')),
    path('api/permissions', include('permissions.urls')),
    path('api/resumes', include('resumes.urls'))
]
