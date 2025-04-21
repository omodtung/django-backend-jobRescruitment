from users.models import User
from django.db.models import Q


def check_permission(email: str, path: str, method: str, module: str):
    try:
        user = User.objects.get(email=email)
        permissions = user.role.permissions.filter(
            Q(api_path=path) & 
            Q(method=method) & 
            Q(module=module) & 
            Q(is_deleted=False)
        )

        if not permissions.exists():
            return {
                "code": 1,
                "message": "User login không có quyền truy cập!"
            }

        return {
            "code": 0,
            "message": "Pass!"
        }
    except User.DoesNotExist:
        return {
            "code": 1,
            "message": "User login not found!"
        }
    
def check_permission_of_user(email, module, path, method):
    # try:
    #     user = User.objects.get(email=email)
    #     permissions = user.role.permissions.filter(
    #         Q(api_path=path) & 
    #         Q(method=method) & 
    #         Q(module=module) & 
    #         Q(is_deleted=False)
    #     )

    #     if not permissions.exists():
    #         return False

    #     return True
    # except User.DoesNotExist:
    #     return False
    return True