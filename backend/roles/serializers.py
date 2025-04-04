from .models import Role
from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

pathUser = "/api/roles"

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
        return data

    
    def create(self, validated_data):
        validated_data = to_snake_case(validated_data)
        # Check permissions
        # check_result = check_permission(validated_data["created_by"].get("email"), pathUser, "POST")
        # if check_result["code"] == 1:
        #     raise PermissionDenied(detail=check_result["message"])
        
        return super().create(validated_data)  # Gọi create() của ModelSerializer
         
    def update(self, instance, validated_data):
        """
        Mô tả cách hoạt động:
        B1: Convert tên biến thành kiểu snake_case để lưu vào db
        B2: Kiểm tra method -> partial = True -> PATCH | False -> PUT
        B3: Check quyền truy cập người thực hiện tác vụ
        B4: Cập nhật các trường khác từ validated_data vào instance để lưu vào db
        """
        # Convert snake_case
        validated_data = to_snake_case(validated_data)

        # self.parital = True -> PATCH and self.partial = FALSE -> PUT
        # if self.partial:
        #     check_result = check_permission(validated_data["updated_by"].get("email"), pathUser, "PATCH")
        #     if check_result["code"] == 1:
        #         raise PermissionDenied(detail=check_result["message"])
        # else:
        #     check_result = check_permission(validated_data["updated_by"].get("email"), pathUser, "PUT")
        #     if check_result["code"] == 1:
        #         raise PermissionDenied(detail=check_result["message"])

        # Cập nhật các trường khác
        permission_ids = [permission.id for permission in validated_data.pop("permissions", None)]
        instance.permissions.set(permission_ids)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

        
