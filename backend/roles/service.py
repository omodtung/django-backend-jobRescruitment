from django.db.models import Q
from .models import Role

def find_all(qs: str):
    sort = qs.pop("sort", None)  # Sắp xếp
    population = qs.pop("population", None)  # Nạp dữ liệu quan hệ

    # Lọc dữ liệu
    filters = Q(is_deleted=False) # Taọ đối tượng Q Object chứa điều kiện lọc
    for key, value in qs.items():
        if isinstance(value, list):  # Nếu value là danh sách
            filters &= Q(**{f"{key}__in": value})  # Sử dụng __in để lọc danh sách
        else:
            filters &= Q(**{key: value})

    # Truy vấn dữ liệu + Population
    return Role.objects.filter(filters).select_related(population).order_by(sort)