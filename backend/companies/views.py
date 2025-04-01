from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone
from .services import find_all
from .models import Companies
from .serializers import CompaniesSerializer
from rest_framework.views import APIView    
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
# List all companies or create a new company
class CompaniesList(APIView):
    permission_classes = [AllowAny]  # Không yêu cầu xác thực
    # def get(self, request):
    #     """ Lấy danh sách tất cả công ty """
    #     companies = Companies.objects.all()
    #     serializer = CompaniesSerializer(companies, many=True)
    #     return Response(serializer.data)
    def get(self, request):
        qs = request.GET.dict() # Lấy toàn bộ chuỗi lọc

        # Lay danh sách tham số đặc biệt
        current_page = int(qs.pop("current", 1))  # Mặc định trang 1
        page_size = int(qs.pop("pageSize", 10))  # Mặc định 10 item/trang
        queryset = find_all(qs)
        
        # Tính toán phân trang
        paginator = Paginator(queryset, page_size)
        total_items = paginator.count
        total_pages = paginator.num_pages
        try:
            Companies = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompaniesSerializer(Companies, many=True)

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
        serializer = CompaniesSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()  # Save the company instance
            response_data = {
                "statusCode": status.HTTP_201_CREATED,
                "message": "",
                "data": {
                    "name": company.name,
                    "address": company.address,
                    "description": company.description,
                    "logo": company.logo,
                    "createdBy": company.createdBy,
                    "isDeleted": company.isDeleted,
                    "deletedAt": company.deletedAt,
                    "_id": company.id,  # Assuming `id` is the primary key
                    "createdAt": company.createdAt,
                    "updatedAt": company.updatedAt,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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