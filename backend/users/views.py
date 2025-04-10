from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializers
from .service import find_all, find_one, remove
from copy import deepcopy
from rest_framework.exceptions import PermissionDenied
from utils.CheckUtils import check_permission
from roles.serializers import RoleSerializers
from companies.models import Companies
from roles.models import Role

module = "USER"
path_not_id = "/api/v1/users"
path_by_id = "/api/v1/users/<int:pk>"
class UserList(APIView):
    # permission_classes = [AllowAny]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    
    # helper function
    def get_object(self, pk):
        """Lay danh sach User theo pk"""
        try:
            return User.objects.get(id = pk)
        except User.DoesNotExist:
            return None
    
    def get(self, request):
        qs = request.GET.dict() # Lấy toàn bộ chuỗi lọc

        # Lay danh sách tham số đặc biệt
        current_page = int(qs.pop("current", 1))  # Mặc định trang 1
        page_size = int(qs.pop("pageSize", 10))  # Mặc định 10 item/trang

        # Truy vấn dữ liệu + Population
        queryset = find_all(qs)
        
        # Tính toán phân trang
        paginator = Paginator(queryset, page_size)
        total_items = paginator.count
        total_pages = paginator.num_pages

        # Lấy dữ liệu trang hiện tại
        try:
            users = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializers(users, many=True)
        data = serializer.data

        for i, user_data in enumerate(data):
            user = serializer.instance[i]
            user_data["role"] = RoleSerializers(user.role).data if user.role else None

        # Trả về kết quả đã cập nhật
        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Fetch List User with paginate----",
            "data": {
                "meta": {
                    "current": current_page,
                    "pageSize": page_size,
                    "pages": total_pages,
                    "totals": total_items,
                },
                "result": data  # <-- dùng `data` đã cập nhật
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
            "_id": user.id,
            "email": user.email
        }
        data["createdBy"] = {
            "_id": user.id,
            "email": user.email
        }
        data["register"] = False
        
        # Kiem tra bien company va role
        if isinstance(data["company"], dict):
            company_id = data["company"].get("_id")
            if not company_id:
                data["company"] = None
            else:
                data["company"] = int(company_id)
        if isinstance(data["role"], dict):
            company_id = data["role"].get("_id")
            if not company_id:
                data["role"] = None
            else:
                data["role"] = int(company_id)

        serializer = UserSerializers(data=data)
        if serializer.is_valid():
            result = serializer.save()
            if result["code"] == 1:
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response({
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach User theo pk"""
        try:
            return User.objects.get(id = pk)
        except User.DoesNotExist:
            return None
    
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

        # Handle role
        if "role" in data and isinstance(data["role"], dict):
            role_id = data["role"].get("_id")
            if role_id:
                try:
                    data["role"] = role_id if role_id else None
                except Role.DoesNotExist:
                    return Response({
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "message": "Khong tim thay role!"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                data["role"] = None
       
        user_update = self.get_object(pk)
       
        # Truyen partical = True -> Use update by PATCH
        serializer = UserSerializers(user_update, data=data, partial=True)
        
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
    