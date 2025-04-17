from .models import Role
from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework import status


module = "ROLE"
path_not_id = "/api/v1/roles"
path_by_id = "/api/v1/roles/<int:pk>"

class RoleSerializers(serializers.ModelSerializer):
    # Custom ten bien truoc khi response
    _id = serializers.JSONField(source="id", required=False, read_only=False)
    isActive = serializers.BooleanField(source="is_active", required=False, read_only=False)
    createdBy = serializers.JSONField(source="created_by", required=False, read_only=False)
    updatedBy = serializers.JSONField(source="updated_by", required=False, read_only=False)
    createdAt = serializers.DateTimeField(source="created_at", required=False, read_only=False)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False, read_only=False)
    deletedBy = serializers.JSONField(source="deleted_by", required=False, read_only=False)
    deletedAt = serializers.DateTimeField(source="deleted_at", required=False, read_only=False)
    isDeleted = serializers.BooleanField(source="is_deleted", required=False, read_only=False)

    class Meta:
        model = Role  
        fields = [
            "_id", "name", "description", "isActive", "permissions", "createdBy", "updatedBy", "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted"
        ]

    def validate_permissions(self, data):
        # Kiểm tra tất cả các quyền truyền vào có tồn tại trong CSDL không
        permission_ids = data or []

        if permission_ids:
            if any(isinstance(item, Permissions) for item in permission_ids):
                # Nếu dữ liệu truyền vào đã được convert thành QuerySet, cần lấy ra ID của chúng
                permission_ids = [perm.id for perm in permission_ids]

            # Lấy tất cả các permission ID hiện có trong DB
            existing_permissions = Permissions.objects.filter(id__in=permission_ids).values_list("id", flat=True)

            # Tìm các permission ID không tồn tại
            missing_permissions = set(permission_ids) - set(existing_permissions)
            
            if missing_permissions:
                raise serializers.ValidationError({
                    "permissions": f"Các quyền sau không tồn tại: {list(missing_permissions)}"
                })
        print("Tra ve gia tri cua permission")
        print("permissions sau khi validate: ", data)
        return data

    def validate_name(self, data):
        print("Bat dau validate_name")
        print("data: ", data)
        if data == "Super Admin":
            raise serializers.ValidationError("Không được trùng tên Role của Super Admin!")
        return data

    def create(self, validated_data):
        # Check permissions
        # check_result = check_permission(validated_data["created_by"].get("email"), path_not_id, "POST", module)
        # if check_result["code"] == 1:
        #     check_result.update({
        #             "statusCode": status.HTTP_403_FORBIDDEN,
        #         })
        #     return check_result
        
        new_role = super().create(validated_data)
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Role create successful!",
                "data": self.__class__(new_role).data
            }
         
    def update(self, instance, validated_data):
        # Check đối tượng cần update có tồn tại
        if not instance:
            return {
                "code": 4,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Role not found!"
            }
        
        # Check đối tượng cần update có phải role Super Admin
        if instance.name == "Super Admin":
            return {
                "code": 3,
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": "Không được thay đổi Role của Super Admin!"
            }


        # Cập nhật các trường khác
        if "permissions" in validated_data:
            permission_ids = [permission.id for permission in validated_data.pop("permissions", None)]
            instance.permissions.set(permission_ids)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Role update successful!",
            "data": self.__class__(instance).data
        }
    
    def delete(self, user_login: list):
        if not self.instance:
            return {
                    "code": 4,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "User not found!"
                }

        # Check đối tượng cần update có phải role Super Admin
        if self.instance.name == "Super Admin":
            return {
                "code": 3,
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": "Không được thay đổi Role của Super Admin!"
            }
        
        instance_deleted = self.instance.soft_delete(user_login)
        data = self.__class__(instance_deleted).data
        return {
            "code": 0,
            "message": "Delete user success!",
            "data": data
        }

        
