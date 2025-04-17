from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

def get_error_message(errors):
    try:
        if isinstance(errors, (ReturnDict, dict)):
            for val in errors.values():
                if isinstance(val, list) and val:
                    return str(val[0])
                return str(val)
        if isinstance(errors, list) and errors:
            return str(errors[0])
    except Exception as e:  
        return f"Lỗi xử lý thông điệp: {e}"

    return "Lỗi không xác định"