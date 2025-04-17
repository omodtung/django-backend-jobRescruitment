from permissions.models import Permissions
from users.models import User
from roles.models import Role

def create_permissions():
    permissions = {
        "COMPANIES": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/companies", "module": "COMPANIES"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/companies", "module": "COMPANIES"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/companies/:id", "module": "COMPANIES"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/companies/:id", "module": "COMPANIES"},
        },
        "JOBS": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/jobs", "module": "JOBS"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/jobs", "module": "JOBS"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/jobs/:id", "module": "JOBS"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/jobs/:id", "module": "JOBS"},
        },
        "PERMISSIONS": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/permissions", "module": "PERMISSIONS"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/permissions", "module": "PERMISSIONS"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/permissions/:id", "module": "PERMISSIONS"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/permissions/:id", "module": "PERMISSIONS"},
        },
        "RESUMES": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/resumes", "module": "RESUMES"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/resumes", "module": "RESUMES"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/resumes/:id", "module": "RESUMES"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/resumes/:id", "module": "RESUMES"},
        },
        "ROLES": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/roles", "module": "ROLES"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/roles", "module": "ROLES"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/roles/:id", "module": "ROLES"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/roles/:id", "module": "ROLES"},
        },
        "USERS": {
            "GET_PAGINATE": {"method": "GET", "apiPath": "/api/v1/users", "module": "USERS"},
            "CREATE": {"method": "POST", "apiPath": "/api/v1/users", "module": "USERS"},
            "UPDATE": {"method": "PATCH", "apiPath": "/api/v1/users/:id", "module": "USERS"},
            "DELETE": {"method": "DELETE", "apiPath": "/api/v1/users/:id", "module": "USERS"},
        },
    }

    permission_is_created = []
    for module, action in permissions.items():
        for key, value in action.items():
            permission, created = Permissions.objects.get_or_create(method=value["method"], api_path=value["apiPath"], module=value["module"], name=key)
            if created:
                print(f"Đã tạo mới permission: {key} {value}")
            permission_is_created.append(permission)
    return permission_is_created

def create_super_admin(permission_is_created):
    # Tạo role Super Admin nếu chưa tồn tại
    role_super_admin, created = Role.objects.get_or_create(
        name="Super Admin",
        defaults={"description": "Super Admin Role"}
    )

    # Nếu role không tồn tại, tạo và gán permissions vào role
    role_super_admin.permissions.set(permission_is_created)
    role_super_admin.save()
    
    # Kiểm tra và tạo tài khoản Super Admin nếu chưa tồn tại
    user_super_admin, created = User.objects.get_or_create(
        email="superadmin@gmail.com",
        defaults={
            "name": "Super Admin",
            "role": role_super_admin,
            "password": "superadmin@gmail.com",
            "age": None,
            "gender": "male",
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
        print("Super Admin account already exists.")

def create_user():
    """ Tao role User """
    role_user, created = Role.objects.get_or_create(
        name="User",
        defaults={"description": "User Role"}
    )
    # Nếu role không tồn tại, gán permissions vào role
    if not created:
        print("User role already exists.")

def run_initial_setup():
    print("Running initial setup...")
    permission_is_created = create_permissions()
    create_super_admin(permission_is_created)
    create_user()
    