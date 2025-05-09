from .models import Resume
from rest_framework import serializers, status
from django.utils import timezone
from companies.models import Companies
from users.models import User
from jobs.models import Job
from companies.serializers import CompaniesSerializer
from jobs.serializers import JobSerializers
from utils.Convert import to_snake_case
from utils.CheckUtils import check_permission
from users.serializers import UserSerializers


module = "RESUME"
path_not_id = "/api/v1/resumes"
path_by_id = "/api/v1/resumes/<int:pk>"

class ResumeSerializers(serializers.ModelSerializer):
    _id = serializers.JSONField(source="id", required=False, read_only=False)

    companyId = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Companies.objects.all(),
        write_only=True
    )
    company = CompaniesSerializer(read_only=True)

    jobId = serializers.PrimaryKeyRelatedField(
        source='job',
        queryset=Job.objects.all(),
        write_only=True
    )
    job = JobSerializers(read_only=True)

    startDate = serializers.DateTimeField(source="start_date", required=False, read_only=False)
    endDate = serializers.DateTimeField(source="end_date", required=False, read_only=False)
    
    createdBy = serializers.JSONField(source="created_by", required=False, read_only=False)
    updatedBy = serializers.JSONField(source="updated_by", required=False, read_only=False)
    
    createdAt = serializers.DateTimeField(source="created_at", required=False, read_only=False)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False, read_only=False)
    deletedBy = serializers.JSONField(source="deleted_by", required=False, read_only=False)
    deletedAt = serializers.DateTimeField(source="deleted_at", required=False, read_only=True)
    isDeleted = serializers.BooleanField(source="is_deleted", required=False, read_only=False)

    userId = serializers.PrimaryKeyRelatedField(
        source='user',  # ánh xạ đến field user trong model
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        # write_only=True
    )

    # user = UserSerializers(read_only=True)

    class Meta:
        model = Resume  
        fields = [
            "_id", "email", "userId", "user","companyId", "company", "jobId", "job", "history", "url", "status",
            "startDate", "endDate",
            "createdAt", "updatedAt", "createdBy", "updatedBy",
            "deletedBy", "deletedAt", "isDeleted"
        ]


    def validate_companyId(self, company):
        if not company:
            return company
        if not Companies.objects.filter(id=company.id).exists():
            raise serializers.ValidationError("Company không tồn tại.")
        return company
    
    def validate_jobId(self, job):
        if not job:
            return job
        if not Job.objects.filter(id=job.id).exists():
            raise serializers.ValidationError("Job không tồn tại.")
        return job
    
    def validate_userId(self, user):
        if not user:
            return user
        if not User.objects.filter(id=user.id).exists():
            raise serializers.ValidationError("User không tồn tại.")
        if Resume.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("User đã có resume tồn tại.")
        return user

    def create(self, validated_data):
        print("validated_data resume: ",validated_data)
        validated_data["status"] = "PENDING"
        new_resume = super().create(validated_data)
        data = self.__class__(new_resume).data
        return {
                "code": 0,
                "statusCode": status.HTTP_201_CREATED,
                "message": "Resume create successful!",
                "data": data
            }

    def update(self, instance, validated_data):
        # Check đối tượng cần update có tồn tại
        if not instance:
            return {
                "code": 2,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Resume not found!"
            }

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Lưu lại đối tượng đã được cập nhật
        data = self.__class__(instance).data
        # data["company"] = CompaniesSerializer(instance.company).data if instance.company else None
        # data["job"] = JobSerializers(instance.job).data if instance.job else None
        return {
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Resume update successful!",
            "data": data
        }