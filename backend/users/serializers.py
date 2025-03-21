from .models import User
from rest_framework import serializers
import re
from django.contrib.auth.hashers import make_password

class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) # Only get password and not return

    class Meta:
        model = User  
        fields = [
            "name", "email", "password", "age", "gender", "address",
            "company", "role", "refresh_token", "created_by", "updated_by", "is_deleted", "deleted_at"
        ]

    def validate(self, data):
        if data.get('email'):
            email = data.get('email')
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            
            if not re.match(email_regex, email):
                raise serializers.ValidationError({"email": "Email không đúng định dạng."})
            
            """ Kiểm tra email đã tồn tại hay chưa """
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email đã được sử dụng.")
        return data

    def create(self, validated_data):
        """Tạo mới user với password được mã hóa."""
        validated_data["password"] = make_password(validated_data["password"])  # Hash mật khẩu
        return super().create(validated_data)  # Gọi create() của ModelSerializer (tự động lưu)
        
