from .models import Role
from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission


class RoleSerializers(serializers.ModelSerializer):
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
            "id", "name", "description", "isActive", "permissions",
            "createdBy", "updatedBy", 
            "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted"
        ]
        # read_only_fields = ["id", "created_at", "updated_at"]
        
    def validate(self, data):
        """
        Nếu dùng validate_permissions thì permissions sẽ bị convert sang Query Set
        Dùng validate để đảm bảo rằng permission không bị convert sang Query Set
        """
        # Kiểm tra tên vai trò phải duy nhất
        if Role.objects.filter(name=data.get("name")).exists():
            raise serializers.ValidationError("Role name is existed!")

        # Kiểm tra tất cả các quyền truyền vào có tồn tại trong CSDL không
        permission_ids = data.get('permissions', [])

        if permission_ids:
            if any(isinstance(item, Permissions) for item in permission_ids):
                # Nếu dữ liệu truyền vào đã được convert thành QuerySet, cần lấy ra ID của chúng
                permission_ids = [perm.id for perm in permission_ids]
            
            print("permission_ids: ", permission_ids)  # Kiểm tra xem có phải là danh sách ID không

            # Lấy tất cả các permission ID hiện có trong DB
            existing_permissions = Permissions.objects.filter(id__in=permission_ids).values_list("id", flat=True)

            # Tìm các permission ID không tồn tại
            missing_permissions = set(permission_ids) - set(existing_permissions)
            
            if missing_permissions:
                raise serializers.ValidationError({
                    "permissions": f"Các quyền sau không tồn tại: {list(missing_permissions)}"
                })
        
        return data  # Trả về dữ liệu hợp lệ nếu tất cả quyền đều tồn tại

    
    def create(self, validated_data):
        validated_data = to_snake_case(validated_data)
        print(validated_data)
        return super().create(validated_data)  # Gọi create() của ModelSerializer
         

        
