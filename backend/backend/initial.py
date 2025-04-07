from permissions.models import Permissions
from users.models import User
from roles.models import Role

def run_initial_setup():
    print("Running initial setup...")
    if Permissions.objects.all() or Role.objects.all() or User.objects.all():
        return
    
    methods_by_id = ["GET", "PUT", "DELETE", "PATCH"]
    methods_not_by_id = ["POST"]
    permissions = {
        "USER": {
            "/api/v1/users",
            "/api/v1/users/<int:pk>"
        },
        "PERMISSION": {
            "/api/v1/permissions",
            "/api/v1/permissions/<int:pk>"
        },
        "ROLE": {
            "/api/v1/roles",
            "/api/v1/roles/<int:pk>",
        },
        "COMPANIES": {
            "/api/v1/companies",
            "/api/v1/companies/<int:pk>",
        },
        "RESUME": {
            "/api/v1/resumes",
            "/api/v1/resumes/<int:pk>",
        },
        "FILE": {
            "/api/v1/files",
            "/api/v1/files/<int:pk>",
        },
        "JOB": {
            "/api/v1/jobs",
            "/api/v1/jobs/<int:pk>",
        },
    }

    permission_is_created = []
    # Tạo permissions cho từng modeule với method và endpoint
    for module, paths in permissions.items():
        for path in paths:
            if path.endswith("<int:pk>"):
                for method in methods_by_id:
                    permission_name = f"{module}_{method}_{path}"
                    permission, created = Permissions.objects.get_or_create(module=module, method=method, api_path=path)
                    if created:
                        permission_is_created.append(permission)
                        print(f"Created permission: {permission_name}")
            else:
                for method in methods_not_by_id:
                    permission_name = f"{module}_{method}_{path}"
                    permission, created = Permissions.objects.get_or_create(module=module, method=method, api_path=path)
                    if created:
                        permission_is_created.append(permission)
                        print(f"Created permission: {permission_name}")

    # Tạo role Super Admin nếu chưa tồn tại
    role_super_admin, created = Role.objects.get_or_create(
        name="Super Admin",
        defaults={"description": "Super Admin Role"}
    )

    # Nếu role không tồn tại, tạo và gán permissions vào role
    if created:
        role_super_admin.permissions.set(permission_is_created)
        role_super_admin.save()
        print("Super Admin role created and permissions assigned.")
    else:
        print("Super Admin role already exists.")
    
    # Kiểm tra và tạo tài khoản Super Admin nếu chưa tồn tại
    user_super_admin, created = User.objects.get_or_create(
        email="superadmin@gmail.com",
        defaults={
            "name": "Super Admin",
            "role": role_super_admin,
            "password": "superadmin@gmail.com",
            "age": None,
            "gender": "male",
            "is_active": True,
            "is_deleted": False,
            "is_superuser": True,
            "is_active": True,
            "is_staff": True,
            "created_by": None,
            "updated_by": None,
            "refresh_token": None,
            "address": "",
        }
    )

    # Nếu tài khoản chưa tồn tại thì tạo mới và gán mật khẩu
    if created:
        user_super_admin.set_password("superadmin@gmail.com")
        user_super_admin.save()
        print("Super Admin account created.")
    else:
        # Nếu tài khoản đã tồn tại, có thể kiểm tra và thay đổi mật khẩu nếu cần
        if user_super_admin.check_password("superadmin@gmail.com") == False:
            user_super_admin.set_password("superadmin@gmail.com")
            user_super_admin.save()
            print("Password updated for Super Admin.")
        else:
            print("Super Admin account already exists.")

    """ Tao role User """
    role_user, created = Role.objects.get_or_create(
        name="User",
        defaults={"description": "User Role"}
    )
    # Nếu role không tồn tại, gán permissions vào role
    if created:
        # Lọc chỉ các permission có method là GET
        get_permissions = [permission for permission in permission_is_created if permission.method == "GET"]

        # Gán permissions GET cho role_user
        role_user.permissions.set(get_permissions)
        role_user.save()
        print("User role created and GET permissions assigned.")
    else:
        print("User role already exists.")
    