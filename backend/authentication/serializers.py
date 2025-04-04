from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .service import save_refresh_token_when_user_login
# from user.

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Thêm thông tin user vào token nếu muốn
        token['name'] = user.name
        token['email'] = user.email
        
        return token
    
    def validate(self, attrs):
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
