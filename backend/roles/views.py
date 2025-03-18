from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Role
from .serializers import RoleSerializers

# Create your views here.

class RoleList(APIView):
    def get(self, request):
        """Lấy danh sách các Role"""
        roleList = Role.objects.all()
        serializer = RoleSerializers(roleList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ Tạo Role mới """
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
    