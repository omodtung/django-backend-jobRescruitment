from .models import Role
from permissions.models import Permissions
from rest_framework import serializers

class RoleSerializers(serializers.ModelSerializer):

    class Meta:
        model = Role  
        fields = [
            "id", "name", "description", "is_active", "permissions",
            "created_at", "updated_at", "created_by", "updated_by",
            "is_deleted", "deleted_at", "deleted_by"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """ Kiểm tra tên vai trò phải duy nhất """
        if Role.objects.filter(name=data.get('name')).exists():
            raise serializers.ValidationError("Tên vai trò đã tồn tại.")
        
        if data.get('is_deleted') and not data.get('deleted_at'):
                raise serializers.ValidationError("`deleted_at` must be set when soft-deleting a company.")
        
        """ Kiểm tra quyền có tồn tại hay không trước khi tạo Role """
        if "permissions" in data:
            permission_ids = data["permissions"]
            existing_permissions = Permissions.objects.filter(id__in=permission_ids).values_list("id", flat=True)

            # Tìm quyền nào không tồn tại
            missing_permissions = set(permission_ids) - set(existing_permissions)
            if missing_permissions:
                raise serializers.ValidationError({
                    "errors": f"Các quyền sau không tồn tại: {list(missing_permissions)}"
                })
        
        return data
    

        
