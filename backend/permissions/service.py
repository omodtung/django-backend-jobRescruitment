from django.db.models import Q
from .models import Permissions
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

pathPermission = "/api/permissions"

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
    return Permissions.objects.filter(filters).select_related(population).order_by(sort)

def find_one(id):
    if not Permissions.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "Permission not found or deleted!"}

    permission = Permissions.objects.get(id=id)

    return {
        "code": 0,
        "message": "Fetch List Permission with paginate----",
        "data": permission
    }

def remove(id, user):
    """ Check quyền truy cập của user """
    # check_result = check_permission(user.email, pathPermission, "POST")
    # if check_result["code"] == 1:
    #     raise PermissionDenied(detail=check_result["message"])

    if not Permissions.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "Permissions not found or deleted!"}
    found = Permissions.objects.get(id=id)
    if found.name == "ADMIN":
        return {"code": 1, "message": "You cannot delete this ADMIN"}
    
    isDeleted = Permissions.objects.get(id=id)
    deleted_by = {
        "id": user.id,
        "email": user.email
    }
    isDeleted.soft_delete(deleted_by)
    isDeleted.save()
    return {
        "code": 0,
        "message": "Delete permission successfully",
        "data": isDeleted
    }