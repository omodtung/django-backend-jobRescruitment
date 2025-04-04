from django.shortcuts import render
from .models import Permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PermissionSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from copy import deepcopy
from django.core.paginator import Paginator
from .service import find_all, remove, find_one


# Create your views here.
class PermissionList(APIView):
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
            roles = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PermissionSerializers(roles, many=True)

        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": 'Fetch List Permission with paginate----',
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

        serializer = PermissionSerializers(data=data)
        if serializer.is_valid():
            new = serializer.save()
            return Response(PermissionSerializers(new).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PermissionDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAuthenticated()]  # POST yêu cầu xác thực
        return [AllowAny()]  # GET không yêu cầu xác thực
    
    # helper function
    def get_object(self, pk):
        """Lay danh sach Permission theo pk"""
        try:
            return Permissions.objects.get(id = pk)
        except Permissions.DoesNotExist:
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
        # Lấy user sau khi xác thực tokentoken
        user = request.user
        # Chuẩn bị dữ liệu để truyền vào serializer
        data = deepcopy(request.data)
        data["updatedBy"] = {
            "id": user.id,
            "email": user.email
        }

        # Lay nguoi dung can update
        permission_update = self.get_object(pk)
        
        """ 
        Cập nhật thông tin UserUser
        Khi gọi UserSerializers(user_update, data=request.data, partial=True) 
        -> Có instance và partial=True sẽ gọi hàm update() phương thức PATCH trong serializer.pypy
        """
        serializer = PermissionSerializers(permission_update, data=data, partial=True)  # partial=True cho phép PATCH
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    