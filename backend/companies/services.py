from django.db.models import Q
from .models import Companies
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

pathCompany = "/api/companies/"

def find_all(qs: dict):
    sort = qs.pop("sort", None)  # Sorting field
    population = qs.pop("population", None)  # Related fields to load

    # Filtering data
    filters = Q(isDeleted=False)  # Use the correct field name from the model
    for key, value in qs.items():
        if isinstance(value, list):  # If the value is a list
            filters &= Q(**{f"{key}__in": value})  # Use __in for filtering lists
        else:
            filters &= Q(**{key: value})

    # Query data with optional population and sorting
    queryset = Companies.objects.filter(filters)
    if population:
        queryset = queryset.select_related(population)
    if sort:
        queryset = queryset.order_by(sort)
    return queryset