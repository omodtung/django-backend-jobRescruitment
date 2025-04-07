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

        # Trả về kết quả giống NestJS
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
        
        print("Bat dau create user")
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
            }, status=statu.HTTP_401_UNAUTHORIZED)
 
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Cap nhat updated_by
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "id": user.id,
            "email": user.email
        }

        # Check permission of user
        # check_result = check_permission(user.email, path_by_id, "PATCH", module)
        # if check_result["code"] == 1:
        #     return Response({
        #         "statusCode": status.HTTP_403_FORBIDDEN,
        #         "message": check_result["message"]
        #     }, status=status.HTTP_403_FORBIDDEN)

        # Lay nguoi dung can update
        # if not User.objects.filter(id=pk, is_deleted=False).exists():
        #     return Response({
        #         "statusCode": status.HTTP_400_BAD_REQUEST,
        #         "message": "User not found!"
        #     }, status=status.HTTP_400_BAD_REQUEST)
        user_update = self.get_object(pk)
        # if user_update.email == "superadmin@gmail.com" or user_update.is_superuser == True:
        #     return Response({
        #         "statusCode": status.HTTP_403_FORBIDDEN,
        #         "message": "You cannot Update Supder Admin"
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        # Truyen partical = True -> Use update by PATCH
        serializer = UserSerializers(user_update, data=data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Truyen partical = True -> Use update by PATCHpartial=True cho phép PATCH
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
    