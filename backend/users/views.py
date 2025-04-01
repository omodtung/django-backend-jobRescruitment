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

class UserList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
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

        print("user view: ", data)
        """ 
        Tạo user mới 
        Khi gọi UserSerializers(data=request.data) -> không có instance mặc định dùng hàm create() trong serializer.pypy
        """
        serializer = UserSerializers(data=data)
        if serializer.is_valid():
            newUser = serializer.save()
            return Response(UserSerializers(newUser).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Chuẩn bị dữ liệu để truyền vào serializer
        # Cap nhat nguoi tao created_by and updated_by
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "id": user.id,
            "email": user.email
        }

        # Lay nguoi dung can update
        user_id_update = request.data.get("id")
        user_update = self.get_object(user_id_update)
        
        """ 
        Cập nhật thông tin UserUser
        Khi gọi UserSerializers(user_update, data=request.data, partial=True) 
        -> Có instance và partial=True sẽ gọi hàm update() phương thức PATCH trong serializer.pypy
        """
        serializer = UserSerializers(user_update, data=data, partial=True)  # partial=True cho phép PATCH
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
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
    
    def delete(self, request, pk):
        """ Lay user da xac thuc """
        user = request.user
        """ Xóa user """
        response = remove(pk, user)
        if response.get("code") == 1:
            response["statusCode"] = status.HTTP_404_NOT_FOUND
            del response["code"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        response["statusCode"] = status.HTTP_204_NO_CONTENT
        del response["code"]
        return Response(response, status=status.HTTP_204_NO_CONTENT)
    