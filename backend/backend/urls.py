
from django.contrib import admin
from django.urls import path ,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/companies',include('companies.urls')) ,
    path('api/users', include('users.urls')),
    path('api/v1/roles', include('roles.urls')),
    path('api/permissions', include('permissions.urls')),
    path('api/resumes', include('resumes.urls')),
    path('api/v1/auth', include('authentication.urls'), name='token_obtain_pair'),
]
