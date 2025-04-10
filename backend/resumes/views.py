from django.shortcuts import render
from .models import Resume
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ResumeSerializers

# Create your views here.
from django.shortcuts import render
from .models import Resume
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ResumeSerializers
from django.utils import timezone
# from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

def find_all(filters):
    queryset = Resume.objects.all()
    # Apply filters based on the provided dictionary
    for key, value in filters.items():
        queryset = queryset.filter(**{key: value})
    return queryset

class ResumeList(APIView):
    # @permission_classes([IsAuthenticated])
    def get(self, request):
        """Lấy danh sách các Resume"""
        qs = request.GET.dict()  # Lấy toàn bộ chuỗi lọc

        # Lay danh sách tham số đặc biệt
        current_page = int(qs.pop("current", 1))  # Mặc định trang 1
        page_size = int(qs.pop("pageSize", 10))  # Mặc định 10 item/trang
        queryset = find_all(qs)

        # Tính toán phân trang
        paginator = Paginator(queryset, page_size)
        total_items = paginator.count
        total_pages = paginator.num_pages
        try:
            resumes = paginator.page(current_page)
        except:
            return Response(
                {"error": "Page out of range"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ResumeSerializers(resumes, many=True)
        
        # Construct the response
        response_data = {
            "statusCode": 200,
            "message": "Fetch List resume with Paginate",
            "data": {
                "meta": {
                    "current": current_page,
                    "pageSize": page_size,
                    "pages": total_pages,
                    "totals": total_items
                },
                "result": serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

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
