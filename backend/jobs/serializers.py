from .models import Job
from roles.models import Role
from companies.models import Companies
from rest_framework import serializers
from companies.serializers import CompaniesSerializer
from utils.CheckUtils import check_permission
from rest_framework import status

module = "JOB"
path_not_id = "/api/v1/jobs"
path_by_id = "/api/v1/jobs/<int:pk>"

class JobSerializers(serializers.ModelSerializer):
    # Setup ten key truoc khi tra ve client
    _id = serializers.JSONField(source="id", required=False, read_only=False)

    companyId = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Companies.objects.all(),
        write_only=True
    )
    company = CompaniesSerializer(read_only=True)

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
            "_id", "name", "skills","companyId", "company", "location", "salary", "quantity",
            "level", "description", "startDate", "endDate", "createdBy", "updatedBy", 
            "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted", "isActive"
        ]
    
    # def validate_company(self, company):
    #     if not company:
    #         return company
    #     if not Companies.objects.filter(id=company._id).exists():
    #         raise serializers.ValidationError("Company không tồn tại.")
    #     return company


    def create(self, validated_data):
        new_job = super().create(validated_data)
        data = self.__class__(new_job).data
        # data["company"] = CompaniesSerializer(new_job.company).data if new_job.company else None
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Job create successful!",
                "data": data
            }
    
    def update(self, instance, validated_data):
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
        data = self.__class__(instance).data
        data["company"] = CompaniesSerializer(instance.company).data if instance.company else None
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Job update successful!",
            "data": data
        }
        
    def delete(self, user_login: list):
        if not self.instance:
            return {
                    "code": 4,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "User not found!"
                }
        
        instance_deleted = self.instance.soft_delete(user_login)
        data = self.__class__(instance_deleted).data
        return {
            "code": 0,
            "message": "Delete user success!",
            "data": data
        }
