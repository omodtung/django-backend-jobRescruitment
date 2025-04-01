from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from .service import find_all
from django.core.paginator import Paginator
from copy import deepcopy

# Create your views here.

class RoleList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
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
        print("data: ", data)

        serializer = RoleSerializers(data=request.data)
        if serializer.is_valid():
            newRole = serializer.save()
            return Response(RoleSerializers(newRole).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleDetail(APIView):
    # helper function
    def get_object(self, pk):
        """Lay danh sach Role theo pk"""
        try:
            return Role.objects.get(id = pk)
        except Role.DoesNotExist:
            return None
       
    # Endpoint GET    
    def get(self, request, pk):
        """Lay thong tin chi tiet cua Role"""
        role = self.get_object(pk)
        if role is None:
            return Response({"error": "Role not found"}, status = status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializers(role)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, pk):
        """ Cập nhật thông tin Role """
        role = self.get_object(pk)
        if role is None:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializers(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """ Xóa Role """
        role = self.get_object(pk)
        if role is None:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    