from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from .service import find_all, remove, find_one
from django.core.paginator import Paginator
from copy import deepcopy
from utils.CheckUtils import check_permission

# Create your views here.
module = "ROLE"
path_not_id = "/api/v1/roles"
path_by_id = "/api/v1/roles/<int:pk>"
class RoleList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Role theo pk"""
        try:
            return Role.objects.get(id = pk)
        except Role.DoesNotExist:
            return None

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
            roles = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RoleSerializers(roles, many=True)

        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": 'Fetch List User with paginate----',
            "data": {
                "meta": {
                    "current": current_page,
                    "pageSize": page_size,
                    "pages": total_pages,
                    "totals": total_items,
                },
            "result": serializer.data
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "User chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
 
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Cap nhat nguoi tao created_by and updated_by
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "id": user.id,
            "email": user.email
        }
        data["createdBy"] = {
            "id": user.id,
            "email": user.email
        }

        print("Bat dau create role")
        serializer = RoleSerializers(data=data)
        if serializer.is_valid():
            result = serializer.save()
            if result["code"] == 1:
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response({
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

class RoleDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Role theo pk"""
        try:
            return Role.objects.get(id = pk)
        except Role.DoesNotExist:
            return None
        
    def patch(self, request, pk):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "User chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Chuẩn bị dữ liệu để truyền vào serializer
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "id": user.id,
            "email": user.email
        }

        # Lay nguoi dung can update
        role_update = self.get_object(pk)
        # Truyen partical = True -> Use update by PATCH
        serializer = RoleSerializers(role_update, data=data, partial=True)  # partial=True cho phép PATCH
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
       
    # Endpoint GET    
    def get(self, request, pk):
        """Lay thong tin chi tiet cua User"""
        reponse = find_one(pk)
        if reponse.get("code") == 1:
            reponse["statusCode"] = status.HTTP_404_NOT_FOUND
            del reponse["code"]
            return Response(reponse, status = status.HTTP_404_NOT_FOUND)
        reponse["statusCode"] = status.HTTP_200_OK
        del reponse["code"]
        return Response(reponse, status = status.HTTP_200_OK)
    
    def delete(self, request, pk):
        if not request.user:
            return Response({
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "massage": "User chưa xác thực!"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        """ Lay user da xac thuc """
        user = request.user

        """ Xóa role """
        response = remove(pk, user, path_by_id, "DELETE", module)
        if response["code"] == 1:
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        if response["code"] == 2:
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        return Response(response, status=status.HTTP_204_NO_CONTENT)
    