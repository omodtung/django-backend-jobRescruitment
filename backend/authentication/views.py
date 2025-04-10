from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .service import save_refresh_token_when_user_login, get_user_from_refresh_token
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializers
from copy import deepcopy
from permissions.serializers import PermissionSerializers



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            """ Django tự động tạo refresh token"""
            refresh_token = response.data.pop("refresh")
            new_access_token = response.data.pop("access")

            if refresh_token:
                user = get_user_from_refresh_token(refresh_token)
                save_refresh_token_when_user_login(user.email, refresh_token)
            
            # Thêm thông điệp tùy chỉnh
            response.data["message"] = "Get User by refresh token"
            response.data["statusCode"] = 200
            response.data["email"] = user.email
            response.data["refresh_token"] = refresh_token
            response.data["access_token"] = new_access_token
        # Trả về phản hồi đã được tùy chỉnh
        return Response(response.data, status=status.HTTP_200_OK)
    
class AccountApiView(APIView):
    permission_classes = [IsAuthenticated]

    # helper function
    def get_object(self, pk):
        """Lay danh sach User theo pk"""
        try:
            return User.objects.get(id = pk)
        except User.DoesNotExist:
            return None
    # def post(self, request):  
    def get(self, request):
        user = request.user
        if not user:
            return Response("User not found!", status=status.HTTP_404_NOT_FOUND)
        role = user.role
        permissions = role.permissions.all()
        print("Permission: ", permissions)
        # print("PermissionSerializers(permissions, many=True).data", PermissionSerializers(permissions, many=True).data)
        permission_ids = [permission["_id"] for permission in PermissionSerializers(permissions, many=True).data]
        
        return Response({
            "statusCode": 200,
            "message": "Get user information",
            "data": {
                "user": {
                    "_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": {
                        "_id": role.id,
                        "name": role.name,
                        "permissions": permission_ids,
                    },
                    "permissions": PermissionSerializers(permissions, many=True).data
                }

              
            }
        }, status=status.HTTP_200_OK)
    
class RegistertApiView(APIView):
    permission_classes = [AllowAny]

    # helper function
    def get_object(self, pk):
        """Lay danh sach User theo pk"""
        try:
            return User.objects.get(id = pk)
        except User.DoesNotExist:
            return None
        
    def post(self, request):
        data = deepcopy(request.data)
        data["register"] = True
        serializer = UserSerializers(data=data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response({
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)