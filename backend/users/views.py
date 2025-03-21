from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from django.core.paginator import Paginator
from .models import User
from .serializers import UserSerializers

# Create your views here.

class UserList(APIView):
    def get(self, request):
        """Lấy danh sách các User"""
        # userList = User.objects.all()
        # serializer = UserSerializers(userList, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        # Lay danh sach query
        current_page = int(request.GET.get("current", 1))  # Mặc định trang 1
        page_size = int(request.GET.get("pageSize", 10))  # Mặc định 10 item/trang
        sort = request.GET.get("sort", "id")  # Sắp xếp theo ID nếu không có
        qs = request.GET.get("qs", "")  # Chuỗi lọc

        # Lọc dữ liệu
        filters = Q() # Taọ đối tượng Q Object chứa điều kiện lọc
        if "name" in request.GET:
            filters &= Q(name__icontains=request.GET["name"]) # Thêm điều kiện tìm kiếm theo tên
        if "email" in request.GET:
            filters &= Q(email__icontains=request.GET["email"]) # Thêm điều kiện tìm kiếm theo email

        # Truy vấn dữ liệu + Population
        # queryset = User.objects.filter(filters).select_related("role").order_by(sort)
        queryset = User.objects.filter(filters).order_by(sort)


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
            "meta": {
                "current": current_page,
                "pageSize": page_size,
                "pages": total_pages,
                "totals": total_items,
            },
            "result": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """ Tạo user mới """
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            newUser = serializer.save()
            return Response(UserSerializers(newUser).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
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
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"}, status = status.HTTP_404_NOT_FOUND)
        serializer = UserSerializers(user)
        return Response(serializer.data, status = status.HTTP_200_OK)

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
    
    def delete(self, request, pk):
        """ Xóa user """
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    