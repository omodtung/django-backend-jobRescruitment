from django.db.models import Q
from .models import Role
from utils.CheckUtils import check_permission
from rest_framework import status
from .serializers import RoleSerializers

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
        return {"code": 1, "message": "Role not found or deleted!"}

    role = Role.objects.get(id=id)
    # permissions = [permission.id for permission in role.permissions.all()]

    return {
        "code": 0,
        "message": "Fetch List User with paginate----",
        "data": RoleSerializers(role).data
    }

def remove(id, user, path, method, module):
    """ Check quyền truy cập của user """
    check_result = check_permission(user.email, path, method, module)
    if check_result["code"] == 1:
        check_result.update({
            "statusCode": status.HTTP_403_FORBIDDEN,
        })
        return check_result

    if not Role.objects.filter(id=id, is_deleted=False).exists():
        return {
            "code": 2,
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Role not found or deleted!"
        }
    isDeleted = Role.objects.get(id=id)
    if isDeleted.name == "Super Admin":
        return {
            "code": 1, 
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "You cannot delete this Super Admin"
        }
    
    deleted_by = {
        "_id": user.id,
        "email": user.email
    }
    isDeleted.soft_delete(deleted_by)
    isDeleted.save()
    return {
        "code": 0,
        "statusCode": status.HTTP_204_NO_CONTENT,
        "message": "Delete user successfully",
        "data": RoleSerializers(isDeleted).data
    }