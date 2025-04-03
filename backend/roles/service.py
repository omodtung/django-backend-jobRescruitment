from django.db.models import Q
from .models import Role
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

pathUser = "/api/roles"

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

def find_one(id):
    if not Role.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "User not found or deleted!"}

    role = Role.objects.get(id=id)
    permissions = [permission.id for permission in role.permissions.all()]

    return {
        "code": 0,
        "message": "Fetch List User with paginate----",
        "data": {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": permissions
        }
    }

def remove(id, user):
    """ Check quyền truy cập của user """
    # check_result = check_permission(user.email, pathUser, "POST")
    # if check_result["code"] == 1:
    #     raise PermissionDenied(detail=check_result["message"])

    if not Role.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "Role not found or deleted!"}
    found = Role.objects.get(id=id)
    if found.name == "ADMIN":
        return {"code": 1, "message": "You cannot delete this ADMIN"}
    
    isDeleted = Role.objects.get(id=id)
    deleted_by = {
        "id": user.id,
        "email": user.email
    }
    isDeleted.soft_delete(deleted_by)
    isDeleted.save()
    return {
        "code": 0,
        "message": "Delete user successfully",
        "data": {
            "id": isDeleted.id,
            "name": isDeleted.name,
            "description": isDeleted.description
            # 
        }
    }