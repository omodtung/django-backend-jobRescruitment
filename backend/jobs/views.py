from django.shortcuts import render
from .models import Job
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import JobSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from copy import deepcopy
from django.core.paginator import Paginator
from .service import find_all, remove, find_one
from companies.models import Companies
from companies.serializers import CompaniesSerializer

module = "JOB"
path_not_id = "/api/v1/jobs"
path_by_id = "/api/v1/jobs/<int:pk>"
# Create your views here.
class JobList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        qs = request.GET.dict()

        current_page = int(qs.pop("current", 1))
        page_size = int(qs.pop("pageSize", 10))

        # Phan trang
        queryset = find_all(qs)

        # Tinh toan phan trang
        paginator = Paginator(queryset, page_size)
        total_items = paginator.count
        total_pages = paginator.num_pages

        try:
            job = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = JobSerializers(job, many=True)
        data = serializer.data

        for i, job_data in enumerate(data):
            job = serializer.instance[i]
            job_data["company"] = CompaniesSerializer(job.company).data if job.company else None

        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": 'Fetch List Job with paginate----',
            "data": {
                "meta": {
                    "current": current_page,
                    "pageSize": page_size,
                    "pages": total_pages,
                    "totals": total_items,
                },
                "result": data
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "Job chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Lấy user sau khi xác thực tokentoken
        user = request.user

        # Cap nhat nguoi tao created_by and updated_by
        data = deepcopy(request.data)

        data["updatedBy"] = {
            "_id": user.id,
            "email": user.email
        }
        data["createdBy"] = {
            "_id": user.id,
            "email": user.email
        }

        if isinstance(data["company"], dict):
            company_id = data["company"].get("_id")
            if not company_id:
                data["company"] = None
            else:
                data["company"] = int(company_id)

        serializer = JobSerializers(data=data)
        if serializer.is_valid():
            result = serializer.save()
            if result["code"] == 1:
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response({
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
    
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
                "massage": "User chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
 
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Cap nhat updated_by
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "_id": user.id,
            "email": user.email
        }

        user_update = self.get_object(pk)
        
        # Truyen partical = True -> Use update by PATCH
        serializer = JobSerializers(user_update, data=data, partial=True)
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
                "massage": "User chưa xác thực!"
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