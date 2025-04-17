from .models import User
from roles.models import Role
from companies.models import Companies
from companies.serializers import CompaniesSerializer
from roles.serializers import RoleSerializers
from rest_framework import serializers
import re
from django.contrib.auth.hashers import make_password
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework import status

class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) # Only get password and not return
    # Setup ten key truoc khi tra ve client
    _id = serializers.JSONField(source="id", required=False, read_only=False)
    name = serializers.CharField(required=False, allow_blank=True)
    createdBy = serializers.JSONField(source="created_by", required=False, read_only=False)
    updatedBy = serializers.JSONField(source="updated_by", required=False, read_only=False)
    refreshToken = serializers.CharField(source="refresh_token", required=False, read_only=False)
    createdAt = serializers.DateTimeField(source="created_at", required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False, read_only=True)
    deletedBy = serializers.JSONField(source="deleted_by", required=False, read_only=False)
    deletedAt = serializers.DateTimeField(source="deleted_at", required=False, read_only=True)
    isDeleted = serializers.BooleanField(source="is_deleted", required=False, read_only=False)

    # Biến để xác thực coi user đăng ký hay admin tạo user
    # register = serializers.BooleanField(required=False, default=False, write_only=True)

    class Meta:
        model = User  
        fields = [
            "_id", "name", "email", "password", "age", "gender", "address",
            "company", "role", "refreshToken", "createdBy", "updatedBy", 
            "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted"
        ]

    def validate_email(self, value):
        """ Kiểm tra định dạng email """
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, value):
            print("Email không đúng định dạng.")
            raise serializers.ValidationError("Email không đúng định dạng.")

        """ Kiểm tra email đã tồn tại """
        if User.objects.filter(email=value).exists():
            print("Email đã được sử dụng.")
            raise serializers.ValidationError("Email đã được sử dụng.")

        return value
    
    def validate_role(self, role):
        if not role:
            try:
                role = Role.objects.get(name="User")
                return role
            except Role.DoesNotExist:
                return role
        if not Role.objects.filter(id=role.id).exists():
            raise serializers.ValidationError("Role không tồn tại.")
        check_supder_admin_role = Role.objects.get(id=role.id)
        if check_supder_admin_role.name == "Super Admin":
            raise serializers.ValidationError("Đây là role Super Admin không thể thao tác!")
        return role
    
    def validate_company(self, company):
        if not company:
            return company
        if not Companies.objects.filter(id=company.id).exists():
            raise serializers.ValidationError("Company không tồn tại.")
        return company


    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])  # Hash mật khẩu
        else: 
            raise serializers.ValidationError({"password": "Password is required!"})
        new_user = super().create(validated_data)
        data = self.__class__(new_user).data
        data["company"] = CompaniesSerializer(new_user.company).data if new_user.company else None
        data["role"] = RoleSerializers(new_user.role).data if new_user.role else None
        return {
                'code': 0,
                'statusCode': status.HTTP_201_CREATED,
                'message': "Create user success!",
                'data': data
            }
    
    def update(self, instance, validated_data):
        # Check đối tượng cần update có tồn tại
        if not instance:
            return {
                "code": 2,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User not found!"
            }
        
        # Check đối tượng cần update có phải role Super Admin
        if instance.email == "superadmin@gmail.com" or instance.is_superuser == True:
            return {
                "code": 1,
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": "Không được thay đổi Super Admin!"
            }

        # Nếu password có trong dữ liệu, thì mã hóa lại
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Lưu lại đối tượng đã được cập nhật
        data = self.__class__(instance).data
        data["company"] = CompaniesSerializer(instance.company).data if instance.company else None
        data["role"] = RoleSerializers(instance.role).data if instance.role else None
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "User update successful!",
            "data": data
        }

    def delete(self, user_login: list):
        if not self.instance:
            return {
                    "code": 4,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "User not found!"
                }

        # Check đối tượng cần update có phải role Super Admin
        if self.instance.email == "superadmin@gmail.com" or self.instance.is_superuser:
            return {
                "code": 3,
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": "Không được xóa Super Admin!"
            }
        
        instance_deleted = self.instance.soft_delete(user_login)
        data = self.__class__(instance_deleted).data
        return {
            "code": 0,
            "message": "Delete user success!",
            "data": data
        }
        
