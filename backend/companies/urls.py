from django.urls import path
from .views import CompaniesList, CompanyDetail

urlpatterns = [
    path('companies/', CompaniesList.as_view(), name='companies-list'),  # GET (list) và POST (create)
    path('companies/<int:pk>/', CompanyDetail.as_view(), name='company-detail'),  # GET (detail), PUT (update), DELETE (delete)
]