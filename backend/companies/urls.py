from django.urls import path
from .views import CompaniesList, CompanyDetail
#  http://127.0.0.1:8000/api/companies/
urlpatterns = [
    # path('companies/', CompaniesList.as_view(), name='companies-list'),  # GET (list) và POST (create)
    path('', CompaniesList.as_view(), name='companies-list'),  # GET (list) và POST (create)
    path('/<int:pk>', CompanyDetail.as_view(), name='company-detail'),  # GET (detail), PUT (update), DELETE (delete)
]
