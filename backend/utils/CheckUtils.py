from users.models import User
from django.db.models import Q

def check_permission(email: str, path: str, method: str):
    try:
        user = User.objects.get(email=email)
        permissions = user.role.permissions.filter(
            Q(api_path=path) & 
            Q(method=method) & 
            Q(is_deleted=False)
        )

        if not permissions.exists():
            return {
                "code": 1,
                "message": "User không có quyền truy cập!"
            }

        return {
            "code": 0,
            "message": "Pass!"
        }
    except User.DoesNotExist:
        return {
            "code": 1,
            "message": "User not found!"
        }
    