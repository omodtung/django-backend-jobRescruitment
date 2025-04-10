import os
import time
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import mimetypes

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES['fileUpload']:
        file = request.FILES['fileUpload']
        file_name = file.name
        file_size = file.size
        file_type = mimetypes.guess_type(file_name)[0]

        # Validate file type
        allowed_file_types = ['jpg', 'jpeg', 'image/jpeg', 'png', 'image/png', 'application/pdf']
        if file_type not in allowed_file_types:
            return JsonResponse({'error': 'Invalid file type'}, status=422)

        # Validate file size
        max_file_size = 1000 * 500  # 500KB
        if file_size > max_file_size:
            return JsonResponse({'error': 'File size too large'}, status=422)

        folder_type = request.POST.get('folder_type', 'default')
        
        # Generate a unique filename
        ext_name = os.path.splitext(file_name)[1]
        base_name = os.path.splitext(file_name)[0]
        final_name = f"{base_name}-{int(time.time())}{ext_name}"

        file_path = os.path.join('images', folder_type, final_name)
        
        # Save the file
        default_storage.save(file_path, file)

        return JsonResponse({'fileName': final_name}, status=200)
    return JsonResponse({'error': 'No file uploaded'}, status=400)
