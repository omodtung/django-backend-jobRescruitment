from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework import status

module = "PERMISSION"
path_not_id = "/api/v1/permissions"
path_by_id = "/api/v1/permissions/<int:pk>"
class PermissionSerializers(serializers.ModelSerializer):
    _id = serializers.JSONField(source='id', required=False, read_only=True)
    apiPath = serializers.CharField(source='api_path', required=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    createdBy = serializers.JSONField(source='created_by', required=False, default=dict)
    updatedBy = serializers.JSONField(source='updated_by', required=False, default=dict)
    deleteBy = serializers.JSONField(source='delete_by', required=False, default=dict)
    isDeleted = serializers.BooleanField(source='is_deleted', required=False, default=False)
    deletedAt = serializers.DateTimeField(source='deleted_at', required=False, allow_null=True)
    class Meta:
        model = Permissions  
        fields = [
            "_id", "name", "apiPath", "method", "module",
            "createdAt", "updatedAt", "createdBy", "updatedBy",
            "deleteBy", "isDeleted", "deletedAt"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]  # Trường chỉ đọc

    def validate(self, data):
        """Đảm bảo method hợp lệ (GET, POST, PUT, DELETE,...)"""
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if data.get('method').upper() not in valid_methods:
            raise serializers.ValidationError("Method không hợp lệ.")
        
        """Kiểm tra logic dữ liệu đầu vào"""
        if data.get("is_deleted") and not data.get("deleted_at"):
            raise serializers.ValidationError("`deleted_at` phải được đặt khi xóa mềm.")
        return data
    
    def create(self, validated_data):
        validated_data = to_snake_case(validated_data)
        # Check permissions
        check_result = check_permission(validated_data["created_by"].get("email"), path_not_id, "POST", module)
        if check_result["code"] == 1:
            check_result.update({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                })
            return check_result
        
        new_permission = super().create(validated_data)
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Permission create successful!",
                "data": self.__class__(new_permission).data
            }
    
    def update(self, instance, validated_data):
        # Convert snake_case
        validated_data = to_snake_case(validated_data)

        # self.parital = True -> PATCH and self.partial = FALSE -> PUT
        if self.partial:
            check_result = check_permission(validated_data["updated_by"].get("email"), path_by_id, "PATCH", module)
            if check_result["code"] == 1:
                check_result.update({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                })
                return check_result
        else:
            check_result = check_permission(validated_data["updated_by"].get("email"), path_by_id, "PUT", module)
            if check_result["code"] == 1:
                check_result.update({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                })
                return check_result

        # Check đối tượng cần update có tồn tại
        if not instance:
            return {
                "code": 2,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Permission not found!"
            }

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Role update successful!",
            "data": self.__class__(instance).data
        }

    

        
