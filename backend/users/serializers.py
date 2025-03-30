from .models import User
from rest_framework import serializers
import re
from django.contrib.auth.hashers import make_password

class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) # Only get password and not return

    class Meta:
        model = User  
        fields = [
            "id", "name", "email", "password", "age", "gender", "address",
            "company", "role", "refresh_token", "created_by", "updated_by", "is_deleted", "deleted_at"
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

    def create(self, validated_data):
        """Tạo mới user với password được mã hóa."""
        validated_data["password"] = make_password(validated_data["password"])  # Hash mật khẩu
        return super().create(validated_data)  # Gọi create() của ModelSerializer (tự động lưu)
        
