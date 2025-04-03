from .models import User
from roles.models import Role
from companies.models import Companies
from rest_framework import serializers
import re
from django.contrib.auth.hashers import make_password
from utils.Convert import to_snake_case

pathUser = "/api/users"

class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) # Only get password and not return
    # Setup ten key truoc khi tra ve client
    _id = serializers.JSONField(source="id", required=False, read_only=False)
    createdBy = serializers.JSONField(source="created_by", required=False, read_only=False)
    updatedBy = serializers.JSONField(source="updated_by", required=False, read_only=False)
    refreshToken = serializers.CharField(source="refresh_token", required=False, read_only=False)
    createdAt = serializers.DateTimeField(source="created_at", required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", required=False, read_only=True)
    deletedBy = serializers.JSONField(source="deleted_by", required=False, read_only=False)
    deletedAt = serializers.DateTimeField(source="deleted_at", required=False, read_only=True)
    isDeleted = serializers.BooleanField(source="is_deleted", required=False, read_only=False)
    class Meta:
        model = User  
        fields = [
            "_id", "name", "email", "password", "age", "gender", "address",
            "company", "role", "refreshToken", "createdBy", "updatedBy", 
            "createdAt", "updatedAt", "deletedBy", "deletedAt", "isDeleted"
        ]

    def validate_email(self, value):
        """ Kiểm tra định dạng email """
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, value):
            print("Email không đúng định dạng.")
            raise serializers.ValidationError("Email không đúng định dạng.")

        """ Kiểm tra email đã tồn tại """
        if User.objects.filter(email=value).exists():
            print("Email đã được sử dụng.")
            raise serializers.ValidationError("Email đã được sử dụng.")

        return value
    
    def validate_role(self, role):
        """ 
        Do role nhận vào từ client là ForeignKey nên lấy id phải dùng role.id 
        nếu không sẽ mặc định trả về role.name
        """
        if not role:
            try:
                role = Role.objects.get(name="Customer")
                return role.id  # Trả về ID nếu tìm thấy đối tượng
            except Role.DoesNotExist:
                return role
        if not Role.objects.filter(id=role.id).exists():
            raise serializers.ValidationError("Role không tồn tại.")
        return role.id  # ✅ Phải trả về giá trị đã kiểm tra (là ID)
    
    def validate_company(self, company):
        """ 
        Do role nhận vào từ client là ForeignKey nên lấy id phải dùng role.id 
        nếu không sẽ mặc định trả về role.name
        """
        if not company:
            return company
        if not Companies.objects.filter(id=company.id).exists():
            raise serializers.ValidationError("Company không tồn tại.")
        return company.id  # ✅ Phải trả về giá trị đã kiểm tra (là ID)


    def create(self, validated_data):
        """
        Mô tả cách hoạt động:
        B1: Convert tên biến thành kiểu snake_case để lưu vào db
        B2: Chuyển đổi tên thuộc tính nhận vào là role thành role_id để lưu vào db
        B4: Tạo mới user
        """

        # Convert snake_case
        validated_data = to_snake_case(validated_data)
        
        # Convert 'role' to 'role_id'
        validated_data["role_id"] = validated_data.pop("role", None)
        validated_data["company_id"] = validated_data.pop("company", None)

        # Tạo user mới
        validated_data["password"] = make_password(validated_data["password"])  # Hash mật khẩu
        return super().create(validated_data)  # Gọi create() của ModelSerializer
    
    def update(self, instance, validated_data):
        """
        Mô tả cách hoạt động:
        B1: Convert tên biến thành kiểu snake_case để lưu vào db
        B2: Kiểm tra method -> partial = True -> PATCH | False -> PUT
        B3: Chuyển đổi tên thuộc tính nhận vào là role thành role_id để lưu vào db
        B4: Kiểm tra nếu có trường password thì cập nhật lại
        B5: Cập nhật các trường khác từ validated_data vào instance để lưu vào db
        """
        # Convert snake_case
        validated_data = to_snake_case(validated_data)
            
        # Convert 'role' to 'role_id'
        instance.role_id = validated_data.pop("role", None)

        # Nếu password có trong dữ liệu, thì mã hóa lại
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()  # Lưu lại đối tượng đã được cập nhật
        return instance
        
