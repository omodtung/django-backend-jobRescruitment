from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework.exceptions import PermissionDenied

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

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    

        
