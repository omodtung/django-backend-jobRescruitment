from .models import Resume
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework import status

class ResumeSerializers(serializers.ModelSerializer):

    class Meta:
        model = Resume  
        fields = "__all__"

    def validate(self, data):
        """Kiểm tra logic dữ liệu đầu vào"""
        if data.get("is_deleted") and not data.get("deleted_at"):
            raise serializers.ValidationError("`deleted_at` phải được đặt khi xóa mềm.")
        return data

    def create(self, validated_data):
        print("Bat dau create user serializer")
        # Convert snake_case
        # validated_data = to_snake_case(validated_data)
        # todo fix register -> trung 
        # Check permissions
        # check_result = check_permission(validated_data["created_by"].get("email"), path_not_id, "POST", module)
        # if check_result["code"] == 1:
        #     check_result.update({
        #             "statusCode": status.HTTP_403_FORBIDDEN,
        #         })
        #     return check_result
        
        # Convert 'role' to 'role_id'
        # validated_data["role_id"] = validated_data.pop("role", None)
        # validated_data["company_id"] = validated_data.pop("company", None)

        # Tạo user mới
        # validated_data["password"] = make_password(validated_data["password"])  # Hash mật khẩu
        user = self.context['request'].user
        email = user.email
        _id = user.id
        new_resume = Resume.objects.create(
            **validated_data,
            email=email,
            userId=_id,
            status='Pending',
            history=[
                {
                    'status': 'PENDING',
                    'updatedAt': str(timezone.now()),
                    'updatedBy': {
                        '_id': _id,
                        'email': email
                    }
                }
            ],
            createdBy={
                '_id': _id,
                'email': email
            }
        )

        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Role create successful!",
                "data": self.__class__(new_resume).data
            }
