from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

from .views import ResumeList, ResumeDetail, ResumeByUser

urlpatterns = [
    path('', ResumeList.as_view(), name='resume-list'),
    path('/<int:pk>', ResumeDetail.as_view(), name='resume-detail'),
    path('/by-user', ResumeByUser.as_view(), name='resume-by-user'),
]
