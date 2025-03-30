from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializers
from .service import find_all, find_one, remove
from utils.CheckUtils import check_permission

pathUser = "/api/users/"
# Create your views here.

class UserList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    def get(self, request):
        print(request.headers.get('Authorization'))
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
        user = request.user
        check_result = check_permission(user.email, pathUser, "POST")
        if check_result["code"] == 1:
            return Response(check_result["message"], status=status.HTTP_403_FORBIDDEN)
        """ Tạo user mới """
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            newUser = serializer.save()
            return Response(UserSerializers(newUser).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
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

    def put(self, request, pk):
        """ Cập nhật thông tin user """
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializers(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @permission_classes([IsAuthenticated]) # Cần JWT token để truy cập API này
    # def patch(self, request, pk):
    #     """ Cập nhật thông tin user """
    #     user = self.get_object(pk)
    #     if user is None:
    #         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = UserSerializers(user, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = request.user
        check_result = check_permission(user.email, pathUser, "DELETE")
        if check_result["code"] == 1:
            return Response(check_result["message"], status=status.HTTP_403_FORBIDDEN)
        """ Xóa user """
        response = remove(pk, "")
        if response.get("code") == 1:
            response["statusCode"] = status.HTTP_404_NOT_FOUND
            del response["code"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        response["statusCode"] = status.HTTP_204_NO_CONTENT
        del response["code"]
        return Response(response, status=status.HTTP_204_NO_CONTENT)
    