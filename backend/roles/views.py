from django.shortcuts import render

# Create your views here.
from utils.Exception import get_error_message
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from .service import find_all, find_one
from django.core.paginator import Paginator
from copy import deepcopy
from utils.CheckUtils import check_permission_of_user

# Create your views here.
module = "ROLE"
path_not_id = "/api/v1/roles"
path_by_id = "/api/v1/roles/:id"
class RoleList(APIView):
    permission_classes = [IsAuthenticated]
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Role theo pk"""
        try:
            return Role.objects.get(id = pk)
        except Role.DoesNotExist:
            return None

    def get(self, request):
        # Check user login by jwt
        if not request.user:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized! Vui lòng đăng nhập!"}, 
                status=status.HTTP_401_UNAUTHORIZED)
        
            # Check permission
        if check_permission_of_user(request.user.email, module, path_not_id, "GET"):
                # Lấy QueryDict và chuyển thành dict từ request
            qs = request.GET.dict()

            # Truy vấn dữ liệu + Population
            result = find_all(qs)

            if result["statusCode"] == 404:
                return Response(result, status=status.HTTP_404_NOT_FOUND)

            serializer = RoleSerializers(result["data"], many=True)
            
            return Response({
                "code": 0,
                "statusCode": result["statusCode"],
                "message": 'Fetch List Role with paginate----',
                "data": {
                    "meta": {
                        "current": result["currentPage"],
                        "pageSize": result["pageSize"],
                        "pages": result["totalPage"],
                        "total": result["totalItem"],
                    },
                    "result": serializer.data
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "code": 3,
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Forbidden! Bạn không có quyền truy cập vào tài nguyên này!"}, 
            status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request):
            # Check user login by jwt
        if not request.user:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized! Vui lòng đăng nhập!"}, 
                status=status.HTTP_401_UNAUTHORIZED)
        
            # Get user login
        user_login = request.user
            # Add info createdBy, updatedBy to request.data
        data = deepcopy(request.data)
        data["createdBy"] = {
            "_id": user_login.id,
            "email": user_login.email
        }
        data["updatedBy"] = {
            "_id": user_login.id,
            "email": user_login.email
        }

            # Check permission
        if check_permission_of_user(request.user.email, module, path_not_id, "POST"):
                # Create new
            serializer = RoleSerializers(data=data)
            if serializer.is_valid():
                result = serializer.save()
                return Response(result, status=status.HTTP_201_CREATED)
            return Response({
                        "code": 1,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": get_error_message(serializer.errors)
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "code": 3,
            "statusCode": status.HTTP_403_FORBIDDEN,
                         "message": "Forbidden! Bạn không có quyền truy cập vào tài nguyên này!"}, 
                         status=status.HTTP_403_FORBIDDEN)

class RoleDetail(APIView):
    permission_classes = [IsAuthenticated]

    # helper function
    def get_object(self, pk):
        """Lay danh sach Role theo pk"""
        try:
            return Role.objects.get(id = pk)
        except Role.DoesNotExist:
            return None

    def get(self, request, pk):
            # Check user login by jwt
        if not request.user:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized! Vui lòng đăng nhập!"}, 
                status=status.HTTP_401_UNAUTHORIZED)
            # Check permission
        if check_permission_of_user(request.user.email, module, path_by_id, "GET"):
            result = find_one(pk)
            if result["code"] == 4:
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            return Response(result, status=status.HTTP_200_OK)
        return Response({
            "code": 3,
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Forbidden! Bạn không có quyền truy cập vào tài nguyên này!"}, 
            status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk):
            # Check user login by jwt
        if not request.user:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized! Vui lòng đăng nhập!"}, 
                status=status.HTTP_401_UNAUTHORIZED)
        
        user_login = request.user
        data = deepcopy(request.data)
        if not "updatedBy" in data:
            data["updatedBy"] = {
                "_id": user_login.id,
                "email": user_login.email
            }

            # Check permission
        if check_permission_of_user(request.user.email, module, path_by_id, "PATCH"):
            instance_update = self.get_object(pk)

            # Update partial user
            serializer = RoleSerializers(instance_update, data=data, partial=True)
            if serializer.is_valid():
                result = serializer.save()
                if result["code"] == 3:
                    return Response(result, status=status.HTTP_403_FORBIDDEN)
                if result["code"] == 4:
                    return Response(result, status=status.HTTP_404_NOT_FOUND)
                return Response(result, status=status.HTTP_200_OK)
            return Response({
                "code": 1,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": get_error_message(serializer.errors)}, 
                status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "code": 3,
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Forbidden! Bạn không có quyền truy cập vào tài nguyên này!"}, 
            status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, pk):
            # Check user login by jwt
        if not request.user:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "message": "Unauthorized! Vui lòng đăng nhập!"}, 
                status=status.HTTP_401_UNAUTHORIZED)

        deleted_by = {
            "_id": request.user.id,
            "email": request.user.email
        }
    
            # Check permission
        if check_permission_of_user(request.user.email, module, path_by_id, "DELETE"):
            instance_delete = self.get_object(pk)
            serializer = RoleSerializers(instance_delete)
            result = serializer.delete(deleted_by)
            if result["code"] == 4:
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            if result["code"] == 3:
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            return Response(result, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "code": 3,
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Forbidden! Bạn không có quyền truy cập vào tài nguyên này!"}, 
            status=status.HTTP_403_FORBIDDEN)
    