from django.shortcuts import render
from .models import Permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PermissionSerializers

# Create your views here.
class PermissionList(APIView):
    def get(self, request):
        """Lấy danh sách các Permission"""
        PermissionList = Permissions.objects.all()
        serializer = PermissionSerializers(PermissionList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ Tạo Permission mới """
        serializer = PermissionSerializers(data=request.data)
        if serializer.is_valid():
            newPermission = serializer.save()
            return Response(PermissionSerializers(newPermission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionDetail(APIView):
    # helper function
    def get_object(self, pk):
        """Lay danh sach Permission theo pk"""
        try:
            return Permissions.objects.get(id = int(pk))
        except Permissions.DoesNotExist:
            return None
       
    # Endpoint GET    
    def get(self, request, pk):
        """Lay thong tin chi tiet cua Permission"""
        permission = self.get_object(pk)
        if permission is None:
            return Response({"error": "Permission not found"}, status = status.HTTP_404_NOT_FOUND)
        serializer = PermissionSerializers(permission)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, pk):
        """ Cập nhật thông tin Permission """
        permission = self.get_object(pk)
        if permission is None:
            return Response({"error": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PermissionSerializers(permission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """ Xóa Permission """
        permission = self.get_object(pk)
        if permission is None:
            return Response({"error": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)
        permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    