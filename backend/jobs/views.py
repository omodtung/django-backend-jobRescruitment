from django.shortcuts import render
from .models import Job
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import JobSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from copy import deepcopy
from django.core.paginator import Paginator
from .service import find_all, find_one
from companies.models import Companies
from utils.CheckUtils import check_permission_of_user
from utils.Exception import get_error_message

module = "JOB"
path_not_id = "/api/v1/jobs"
path_by_id = "/api/v1/jobs/:id"
# Create your views here.
class JobList(APIView):
    permission_classes = [IsAuthenticated]
 
    # helper function
    def get_object(self, pk):
        """Lay danh sach Job theo pk"""
        try:
            return Job.objects.get(id = pk)
        except Job.DoesNotExist:
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

            serializer = JobSerializers(result["data"], many=True)
            
            return Response({
                "code": 0,
                "statusCode": result["statusCode"],
                "message": 'Fetch List Job with paginate----',
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
        if not "createdBy" in data:
            data["createdBy"] = {
                "_id": user_login.id,
                "email": user_login.email
            }
        if not "updatedBy" in data:
            data["updatedBy"] = {
                "_id": user_login.id,
                "email": user_login.email
            }

        # Kiem tra bien company
        if isinstance(data["company"], dict):
            company_id = data["company"].get("_id")
            if not company_id:
                data["company"] = None
            else:
                data["company"] = int(company_id)

            # Check permission
        if check_permission_of_user(request.user.email, module, path_not_id, "POST"):
                # Create new
            serializer = JobSerializers(data=data)
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
    
class JobDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Job theo pk"""
        try:
            return Job.objects.get(id = pk)
        except Job.DoesNotExist:
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

        # Kiem tra bien company
        if "company" in data and isinstance(data["company"], dict):
            company_id = data["company"].get("_id")
            if company_id:
                try:
                    data["company"] = company_id if company_id else None
                except Companies.DoesNotExist:
                    return Response({
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "message": "Khong tim thay company!"
                        }, status=status.HTTP_404_NOT_FOUND)
            else:
                data["company"] = None

            # Check permission
        if check_permission_of_user(request.user.email, module, path_by_id, "PATCH"):
            instance_update = self.get_object(pk)

            # Update partial user
            serializer = JobSerializers(instance_update, data=data, partial=True)
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
        if not "deletedBy" in request.data:
            deleted_by = {
                "_id": request.user.id,
                "email": request.user.email
            }
        else:
            deleted_by = request.data["deletedBy"]
    
            # Check permission
        if check_permission_of_user(request.user.email, module, path_by_id, "DELETE"):
            instance_delete = self.get_object(pk)
            serializer = JobSerializers(instance_delete)
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
    