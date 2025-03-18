from permissions.models import Permissions
from rest_framework import serializers

class PermissionSerializers(serializers.ModelSerializer):

    class Meta:
        model = Permissions  
        fields = [
            "id", "name", "api_path", "method", "module",
            "created_at", "updated_at", "created_by", "updated_by",
            "delete_by", "is_deleted", "deleted_at"
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
    

        
