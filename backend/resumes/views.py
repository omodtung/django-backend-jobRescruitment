from django.shortcuts import render

from utils.Exception import get_error_message
from .models import Resume
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ResumeSerializers
from utils.CheckUtils import check_permission_of_user
from rest_framework.permissions import AllowAny, IsAuthenticated
from copy import deepcopy
from django.core.paginator import Paginator
from .service import find_all, find_one
from companies.models import Companies
from jobs.models import Job

module = "RESUME"
path_not_id = "/api/v1/resumes"
path_by_id = "/api/v1/resumes/:id"
class ResumeList(APIView):
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

            # serializer = ResumeSerializers(result["data"], many=True)
            
            return Response({
                "code": 0,
                "statusCode": result["statusCode"],
                "message": 'Fetch List Resume with paginate----',
                "data": {
                    "meta": {
                        "current": result["currentPage"],
                        "pageSize": result["pageSize"],
                        "pages": result["totalPage"],
                        "total": result["totalItem"],
                    },
                    "result": result["data"]
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

        # Kiem tra bien company va role
        if isinstance(data["company"], dict):
            company_id = data["company"].get("_id")
            if not company_id:
                data["company"] = None
            else:
                data["company"] = int(company_id)
        if isinstance(data["job"], dict):
            job_id = data["job"].get("_id")
            if not job_id:
                data["job"] = None
            else:
                data["job"] = int(job_id)

            # Check permission
        if check_permission_of_user(request.user.email, module, path_not_id, "POST"):
                # Create new
            serializer = ResumeSerializers(data=data)
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

class ResumeDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Resume theo pk"""
        try:
            return Resume.objects.get(id = pk)
        except Resume.DoesNotExist:
            return None
    
    # Endpoint GET    
    def get(self, request, pk):
        """Lay thong tin chi tiet cua Job"""
        reponse = find_one(pk)
        if reponse.get("code") == 1:
            reponse["statusCode"] = status.HTTP_404_NOT_FOUND
            del reponse["code"]
            return Response(reponse, status = status.HTTP_404_NOT_FOUND)
        reponse["statusCode"] = status.HTTP_200_OK
        del reponse["code"]
        return Response(reponse, status = status.HTTP_200_OK)
    
    def patch(self, request, pk):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "Resume chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
 
        # Lấy user sau khi xác thực tokentoken
        user_login = request.user
        data = deepcopy(request.data)
        # Cap nhat updated_by
        if not "updatedBy" in data:
            data["updatedBy"] = {
                "_id": user_login.id,
                "email": user_login.email
            }

        # Kiem tra bien company va role
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
        if "job" in data and isinstance(data["job"], dict):
            job_id = data["job"].get("_id")
            if job_id:
                try:
                    data["job"] = job_id if job_id else None
                except Job.DoesNotExist:
                    return Response({
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "message": "Khong tim thay job!"
                        }, status=status.HTTP_404_NOT_FOUND)
            else:
                data["company"] = None

        resume_update = self.get_object(pk)
        
        # Truyen partical = True -> Use update by PATCH
        serializer = ResumeSerializers(resume_update, data=data, partial=True)
        if serializer.is_valid():
            result = serializer.save()
            if result["code"] == 1:
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            if result["code"] == 2:
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            return Response(result, status=status.HTTP_200_OK)
        return Response({
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "Resume chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
 

        # Lấy user sau khi xác thực tokentoken
        user = request.user

        """ Xóa user """
        response = remove(pk, user, path_by_id, "DELETE", module)
        if response["code"] == 1:
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        if response["code"] == 2:
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        return Response(response, status=status.HTTP_204_NO_CONTENT)
