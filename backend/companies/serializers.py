from rest_framework import serializers,status
from .models import Companies


pathCompany = "/api/companies/"
class CompaniesSerializer(serializers.ModelSerializer):
    _id = serializers.JSONField(source="id", required=False, read_only=False)

    class Meta:
        model = Companies
        # fields = '__all__'  
        fields = [
            "_id",
            "name",
            "address",
            "description",
            "createdAt",
            "updatedAt",
            "logo",
            "isDeleted",
            "deletedAt",
            "createdBy",
            "updatedBy",
            "deletedBy",
        ]
        # same import feild into  Model 
    
    # def validate(self, data):
    #     if data.get('is_deleted') and not data.get('deleted_at'):
    #         raise serializers.ValidationError("`deleted_at` must be set when soft-deleting a company.")
    #     return data

    # def to_representation(self, instance):
    #     """Customize the serialized output to replace `id` with `_id`."""
    #     representation = super().to_representation(instance)
    #     representation['_id'] = representation.pop('id')  # Replace `id` with `_id`
    #     return representation

    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        new_user = super().create(validated_data)
        data = self.__class__(new_user).data
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
                "message": "Company not found!"
            }

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Lưu lại đối tượng đã được cập nhật
        data = self.__class__(instance).data
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Company update successful!",
            "data": data
        }

    def delete(self, user_login: list):
        if not self.instance:
            return {
                    "code": 4,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "Company not found!"
                }
        
        instance_deleted = self.instance.soft_delete(user_login)
        data = self.__class__(instance_deleted).data
        return {
            "code": 0,
            "message": "Delete company success!",
            "data": data
        }