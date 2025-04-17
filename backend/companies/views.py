from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone
from .services import find_all, find_one
from copy import deepcopy
from .models import Companies
from .serializers import CompaniesSerializer
from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from utils.Exception import get_error_message
from utils.CheckUtils import check_permission_of_user
# List all companies or create a new company

module = "COMPANIES"
path_not_id = "/api/v1/companies"
path_by_id = "/api/v1/companies/:id"
class CompaniesList(APIView):
    # permission_classes = [AllowAny]  # Không yêu cầu xác thực
    permission_classes = [IsAuthenticated]

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

            serializer = CompaniesSerializer(result["data"], many=True)
            
            return Response({
                "code": 0,
                "statusCode": result["statusCode"],
                "message": 'Fetch List Companies with paginate----',
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

        # Check permission
        if check_permission_of_user(request.user.email, module, path_not_id, "POST"):
                # Create new
            serializer = CompaniesSerializer(data=data)
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

# Retrieve, update, or delete a company
class CompanyDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    def get_object(self, pk):
        """ Lấy công ty bằng ID """
        try:
            return Companies.objects.get(id=pk)
        except Companies.DoesNotExist:
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
       
    def put(self, request, pk):
        """ Cập nhật thông tin công ty """
        company = self.get_object(pk)
        if company is None:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompaniesSerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": 200,
                "message": "",
                "data": {
                    "acknowledged": True,
                    "modifiedCount": 1,
                    "upsertedId": None,
                    "upsertedCount": 0,
                    "matchedCount": 1
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ Xóa công ty """
        company = self.get_object(pk)
        if company is None:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        company.delete()

        return Response({
           "statusCode": 200,
           "message": "",
           "data": {
               "deleted": 1
           }
       })
