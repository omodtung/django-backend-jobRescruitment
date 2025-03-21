from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from django.utils import timezone
from .models import Companies
from .serializers import CompaniesSerializer
from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# List all companies or create a new company
class CompaniesList(APIView):
    permission_classes = [AllowAny]  # Không yêu cầu xác thực
    def get(self, request):
        """ Lấy danh sách tất cả công ty """
        companies = Companies.objects.all()
        serializer = CompaniesSerializer(companies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """ Tạo một công ty mới """
        serializer = CompaniesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve, update, or delete a company
class CompanyDetail(APIView):
    permission_classes = [AllowAny]  # Không yêu cầu xác thực
    def get_object(self, pk):
        """ Lấy công ty bằng ID """
        try:
            return Companies.objects.get(pk=pk)
        except Companies.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """ Lấy thông tin chi tiết công ty """
        company = self.get_object(pk)
        if company is None:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompaniesSerializer(company)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """ Cập nhật thông tin công ty """
        company = self.get_object(pk)
        if company is None:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompaniesSerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """ Xóa công ty """
        company = self.get_object(pk)
        if company is None:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)