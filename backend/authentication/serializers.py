from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .service import save_refresh_token_when_user_login
from users.models import User
from rest_framework import serializers
# from user.

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       # Giả sử client gửi 'username' nhưng bạn muốn gán giá trị cho 'email'
        if 'username' in kwargs.get('data', {}):
            print("Can thiệp trước khi gán dữ liệu vào fields")

            # Lấy giá trị 'username' từ data (request)
            username_value = kwargs['data'].get('username')

            # Cập nhật dữ liệu trước khi gán vào fields
            kwargs['data']['email'] = username_value
            del kwargs['data']['username']  # Xóa 'username' đi để không bị trùng
            print("Dữ liệu sau khi thay đổi:", kwargs['data'])

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Thêm thông tin user vào token nếu muốn
        token['name'] = user.name
        token['email'] = user.email
        
        return token
    
    def validate(self, attrs):
        print("Buoc2")
        # Nếu nhận được 'username', đổi tên thành 'email'
        email = attrs.get('email')
        password = attrs.get('password')

        print("email:", email)
        print("password:", password)

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email khong ton tai hoac bi xoa")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Password khong dung")
        
        data = super().validate(attrs)
        accessToken = data.pop('access')
        refreshToken = data.pop('refresh')

        userLogin = save_refresh_token_when_user_login(self.user.email, refreshToken)
        print("User Login; ", userLogin)

        # Custom thong tin response
        data['statusCode'] = 201
        data['message'] = "User login"
        data['data'] = {
            "access_token": accessToken,
            "refresh_token": refreshToken,
            "user": {
                "_id": self.user.id,
                "name": self.user.name,
                "email": self.user.email,
                "role": {
                    "_id": self.user.role.id,
                    "name": self.user.role.name,
                    "permissions": [permission.id for permission in self.user.role.permissions.all()]
                }
            }
        }
        return data
