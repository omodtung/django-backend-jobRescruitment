from django.db.models import Q
from .models import User
from utils.CheckUtils import check_permission
from rest_framework import status
from .serializers import UserSerializers


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
    data = UserSerializers(user).data
    data["role"] = {
        "id": user.role.id if user.role else None,
        "name": user.role.name if user.role else None,
        "description": user.role.description if user.role else None
    }
    return {
        "code": 0,
        "message": "Fetch List User with paginate----",
        "data": data
    }

def remove(id, user, path, method, module):
    """ Check quyền truy cập của user """
    check_result = check_permission(user.email, path, method, module)
    if check_result["code"] == 1:
        check_result.update({
            "statusCode": status.HTTP_403_FORBIDDEN,
        })
        return check_result
    
    if not User.objects.filter(id=id, is_deleted=False).exists():
        return {
            "code": 2,
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "User not found or deleted!"
        }
    
    userIsDeleted = User.objects.get(id=id)
    if userIsDeleted.email == "superadmin@gmail.com" or userIsDeleted.is_superuser == True:
        return {
            "code": 1, 
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "You cannot delete Super Admin"
        }
    
    deleted_by = {
        "_id": user.id,
        "email": user.email
    }
    userIsDeleted.soft_delete(deleted_by)
    userIsDeleted.save()
    return {
        "code": 0,
        "statusCode": status.HTTP_204_NO_CONTENT,
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

