
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/companies', include('companies.urls')),
    path('api/v1/users', include('users.urls')),
    path('api/v1/roles', include('roles.urls')),
    path('api/v1/jobs', include('jobs.urls')),
    path('api/v1/permissions', include('permissions.urls')),
    path('api/v1/resumes', include('resumes.urls')),
    path('api/v1/auth', include('authentication.urls'), name='token_obtain_pair'),
    path('api/v1/files', include('file.urls'))
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
