import os
import time
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
import mimetypes
from utils.Exception import get_error_message
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from copy import deepcopy

# @csrf_exempt
# def upload_file(request):
#     if request.method == 'POST' and request.FILES['fileUpload']:
#         file = request.FILES['fileUpload']
#         file_name = file.name
#         file_size = file.size
#         file_type = mimetypes.guess_type(file_name)[0]

#         # Validate file type
#         allowed_file_types = ['jpg', 'jpeg', 'image/jpeg', 'png', 'image/png', 'application/pdf']
#         if file_type not in allowed_file_types:
#             return JsonResponse({'error': 'Invalid file type'}, status=422)

#         # Validate file size
#         max_file_size = 1000 * 500  # 500KB
#         if file_size > max_file_size:
#             return JsonResponse({'error': 'File size too large'}, status=422)

#         # folder_type = request.POST.get('folder_type', 'default')
#         folder_type = request.headers.get('folder_type', 'default')
        
#         # Generate a unique filename
#         ext_name = os.path.splitext(file_name)[1]
#         base_name = os.path.splitext(file_name)[0]
#         final_name = f"{base_name}-{int(time.time())}{ext_name}"

#         file_path = os.path.join('images', folder_type, final_name)

#         # Check if the folder exists, if not create it
#         folder_path = os.path.dirname(file_path)
#         if not os.path.exists(folder_path):
#             os.makedirs(folder_path)  # Create the directory if it doesn't exist
        
#         # Save the file
#         default_storage.save(file_path, file)

#         return JsonResponse({'fileName': final_name}, status=200)
#     return JsonResponse({'error': 'No file uploaded'}, status=400)

class FileList(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Kiểm tra xem file đã được gửi lên chưa
        if 'fileUpload' not in request.FILES:
            return Response({
                "code": 1,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "No file uploaded",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['fileUpload']
        file_name = file.name
        file_size = file.size
        file_type = mimetypes.guess_type(file_name)[0]

        # Kiểm tra loại file
        allowed_file_types = ['jpg', 'jpeg', 'image/jpeg', 'png', 'image/png', 'application/pdf']
        if file_type not in allowed_file_types:
            return Response({
                "code": 2,
                "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Invalid file type",
                "data": {}
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        print("print(file_type, file_size)", file_type, file_size)
        # Kiểm tra kích thước file
        max_file_size = 1000 * 500  # 500KB
        if file_size > max_file_size:
            return Response({
                "code": 3,
                "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "File size too large",
                "data": {}
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # folder_type = request.headers.get('folder_type', 'default')
        folder_type = request.POST.get('folder_type', 'default')
        print("request.headers", request.POST.get('folder_type'))
        print("folder_type", folder_type)

        # Tạo tên file duy nhất
        ext_name = os.path.splitext(file_name)[1]
        base_name = os.path.splitext(file_name)[0]
        final_name = f"{base_name}-{int(time.time())}{ext_name}"

        # file_path = os.path.join('images', folder_type, final_name)
        file_path = os.path.join(folder_type, final_name)
        # Kiểm tra và tạo thư mục nếu không tồn tại
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Lưu file
        try:
            default_storage.save(file_path, file)
        except Exception as e:
            return Response({
                "code": 4,
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"Error saving file: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Trả về kết quả thành công
        return Response({
            "code": 0,
            "statusCode": status.HTTP_200_OK,
            "message": "Upload file success!",
            "data": {
                'fileName': final_name
            }
        }, status=status.HTTP_200_OK)
