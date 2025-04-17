from permissions.models import Permissions
from rest_framework import serializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework import status

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

    def validate(self, data):
        """Đảm bảo method hợp lệ (GET, POST, PUT, DELETE,...)"""
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if data.get('method').upper() not in valid_methods:
            raise serializers.ValidationError("Method không hợp lệ.")
        
        return data
    
    def create(self, validated_data):
        new_permission = super().create(validated_data)
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Permission create successful!",
                "data": self.__class__(new_permission).data
            }
    
    def update(self, instance, validated_data):
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
            "message": "Permission update successful!",
            "data": self.__class__(instance).data
        }
    
    def delete(self, user_login: list):
        if not self.instance:
            return {
                    "code": 4,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "Permission not found!"
                }
        
        instance_deleted = self.instance.soft_delete(user_login)
        data = self.__class__(instance_deleted).data
        return {
            "code": 0,
            "message": "Delete permission success!",
            "data": data
        }

    

        
