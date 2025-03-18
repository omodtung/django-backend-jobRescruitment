from django.shortcuts import render
from .models import Resume
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ResumeSerializers

# Create your views here.
class ResumeList(APIView):
    def get(self, request):
        """Lấy danh sách các Resume"""
        resumeList = Resume.objects.all()
        serializer = ResumeSerializers(resumeList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ Tạo Resume mới """
        serializer = ResumeSerializers(data=request.data)
        if serializer.is_valid():
            newResume = serializer.save()
            return Response(ResumeSerializers(newResume).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResumeDetail(APIView):
    # helper function
    def get_object(self, pk):
        """Lay danh sach Resume theo pk"""
        try:
            return Resume.objects.get(id = int(pk))
        except Resume.DoesNotExist:
            return None
       
    # Endpoint GET    
    def get(self, request, pk):
        """Lay thong tin chi tiet cua Resume"""
        resume = self.get_object(pk)
        if resume is None:
            return Response({"error": "Resume not found"}, status = status.HTTP_404_NOT_FOUND)
        serializer = ResumeSerializers(resume)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, pk):
        """ Cập nhật thông tin Resume """
        resume = self.get_object(pk)
        if resume is None:
            return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResumeSerializers(resume, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """ Xóa Resume """
        resume = self.get_object(pk)
        if resume is None:
            return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        resume.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    