from .models import Job
from roles.models import Role
from companies.models import Companies
from rest_framework import serializers
import re
from django.contrib.auth.hashers import make_password
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from rest_framework import status

module = "JOB"
path_not_id = "/api/v1/jobs"
path_by_id = "/api/v1/jobs/<int:pk>"

class JobSerializers(serializers.ModelSerializer):
    # Setup ten key truoc khi tra ve client
    _id = serializers.JSONField(source="id", required=False, read_only=False)
    createdBy = serializers.JSONField(source="created_by", required=False, read_only=False)
    updatedBy = serializers.JSONField(source="updated_by", required=False, read_only=False)
    createdAt = serializers.DateTimeField(source="created_at", required=False, read_only=False, allow_null=True)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False, read_only=False, allow_null=True)
    deletedBy = serializers.JSONField(source="deleted_by", required=False, read_only=False)
    deletedAt = serializers.DateTimeField(source="deleted_at", required=False, read_only=False, allow_null=True)
    isDeleted = serializers.BooleanField(source="is_deleted", required=False, read_only=False)
    startDate = serializers.DateTimeField(source= "start_date", required=False, allow_null=True, read_only=False, input_formats=["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"])
    endDate = serializers.DateTimeField(source= "end_date", required=False, allow_null=True, read_only=False, input_formats=["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"])
    isActive = serializers.BooleanField(source= "is_active", required=False, allow_null=True, read_only=False)

    class Meta:
        model = Job  
        fields = [
            "_id", "name", "skills", "company", "location", "salary", "quantity",
            "level", "description", "startDate", "endDate", "createdBy", "updatedBy", 
            "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted", "isActive"
        ]
    
    def validate_company(self, company):
        """ 
        Do role nhận vào từ client là ForeignKey nên lấy id phải dùng role.id 
        nếu không sẽ mặc định trả về role.name
        """
        print("company: ", company)
        if not company:
            return company
        if not Companies.objects.filter(id=company.id).exists():
            raise serializers.ValidationError("Company không tồn tại.")
        return company.id  # ✅ Phải trả về giá trị đã kiểm tra (là ID)


    def create(self, validated_data):
        print("Bat dau tao")
        # Check permissions
        check_result = check_permission(validated_data["created_by"].get("email"), path_not_id, "POST", module)
        if check_result["code"] == 1:
            check_result.update({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                })
            return check_result
        
        # Convert 'company' to 'company_id'
        validated_data["company_id"] = validated_data.pop("company", None)

        new_job = super().create(validated_data)
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Job create successful!",
                "result": self.__class__(new_job).data
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
                "message": "Job not found!"
            }

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Lưu lại đối tượng đã được cập nhật
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Job update successful!",
            "data": self.__class__(instance).data
        }
        
