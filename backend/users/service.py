from django.db.models import Q
from .models import User
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

pathUser = "/api/users"

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
    return User.objects.filter(filters).select_related(population).order_by(sort)

def find_one(id: str):
    if not User.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "User not found or deleted!"}

    user = User.objects.select_related('role').get(id=id)

    return {
        "code": 0,
        "message": "Fetch List User with paginate----",
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": {
                "id": user.role.id if user.role else None,
                "name": user.role.name if user.role else None,
                "description": user.role.description if user.role else None
            }
        }
    }

def remove(id: str, user):
    """ Check quyền truy cập của user """
    check_result = check_permission(user.email, pathUser, "POST")
    if check_result["code"] == 1:
        raise PermissionDenied(detail=check_result["message"])

    if not User.objects.filter(id=id, is_deleted=False).exists():
        return {"code": 1, "message": "User not found or deleted!"}
    foundUser = User.objects.get(id=id)
    if foundUser.email == "admin@gmail.com":
        return {"code": 1, "message": "You cannot delete this user"}
    
    userIsDeleted = User.objects.get(id=id)
    deleted_by = {
        "id": user.id,
        "email": user.email
    }
    userIsDeleted.soft_delete(deleted_by)
    userIsDeleted.save()
    return {
        "code": 0,
        "message": "Delete user successfully",
        "data": {
            "id": userIsDeleted.id,
            "name": userIsDeleted.name,
            "email": userIsDeleted.email,
            "role": {
                "id": userIsDeleted.role.id if userIsDeleted.role else None,
                "name": userIsDeleted.role.name if userIsDeleted.role else None,
                "description": userIsDeleted.role.description if userIsDeleted.role else None
            }
        }
    }

