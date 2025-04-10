
# Chuyển định dạng nếu client gửi camelCase chuyển thành snake_case
import re

def camel_to_snake(name: str) -> str:
    """Chuyển một chuỗi từ camelCase -> snake_case"""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def to_snake_case(data):
    """Đệ quy chuyển tất cả các key từ camelCase -> snake_case"""
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = camel_to_snake(key)
            new_data[new_key] = to_snake_case(value)
        return new_data
    elif isinstance(data, list):
        return [to_snake_case(item) for item in data]
    else:
        return  camel_to_snake(data)
