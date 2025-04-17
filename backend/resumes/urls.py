from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

from .views import ResumeList, ResumeDetail

urlpatterns = [
    path('', ResumeList.as_view(), name='resume-list'),
    path('/<int:pk>', ResumeDetail.as_view(), name='resume-detail'),

]
