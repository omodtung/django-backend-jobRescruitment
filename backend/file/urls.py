from django.urls import path
from . import views
from .views import FileList

urlpatterns = [
    # path('/upload', views.upload_file, name='upload_file'),
    path('/upload', FileList.as_view(), name='upload_file'),
]
