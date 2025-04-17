from django.db.models import Q
from .models import Permissions
from utils.CheckUtils import check_permission
from rest_framework import status
from .serializers import PermissionSerializers
from utils.Convert import to_snake_case
from django.apps import apps
from django.core.paginator import Paginator

def find_all(qs):
    """
    qs: QueryDict (ví dụ request.GET) hoặc dict chứa các tham số:
        - current, pageSize, sort, populate, fields, và các bộ lọc khác
    """
    Permissions = apps.get_model('permissions', 'Permissions')
    model_fields = {f.name for f in Permissions._meta.fields}
    related_fields = {rel.get_accessor_name() for rel in Permissions._meta.related_objects}

    # ─── 1. Parse & validate pagination ───────────────────────────────
    try:
        page_size = int(qs.get('pageSize', 10))
        if page_size <= 0:
            raise ValueError
    except (ValueError, TypeError):
        page_size = 10

    try:
        current_page = int(qs.get('current', 1))
        if current_page <= 0:
            raise ValueError
    except (ValueError, TypeError):
        current_page = 1

    # Remove pagination params so chúng không được xử lý lại ở filters
    params = qs.copy()
    params.pop('pageSize', None)
    params.pop('current', None)

    # ─── 2. Sort ────────────────────────────────────────────────────────
    raw_sort = params.pop('sort', None)
    sort = None
    if isinstance(raw_sort, str):
        # type: ignore
        direction = '-' if raw_sort.startswith('-') else ''
        field = raw_sort.lstrip('-')
        if field in model_fields:
            sort = f"{direction}{field}"
    if not sort:
        sort = 'id'  # default

    # ─── 3. Population (select_related) ────────────────────────────────
    raw_pop = params.pop('populate', None)
    population = raw_pop if raw_pop in related_fields else None

    # ─── 4. Fields (values/only) ───────────────────────────────────────
    raw_fields = params.pop('fields', None)
    fields = []
    if isinstance(raw_fields, str):
        # tách theo dấu phẩy, loại bỏ khoảng trắng
        for f in [f.strip() for f in raw_fields.split(',')]:
            # allow x.y syntax for related field
            if '.' in f:
                root, sub = f.split('.', 1)
                if root in related_fields and sub in {field.name for field in Permissions._meta.get_field(root).related_model._meta.fields}:
                    fields.append(f)
            elif f in model_fields:
                fields.append(f)

    # ─── 5. Build filters ───────────────────────────────────────────────
    filters = Q(is_deleted=False)
    for key, value in params.items():
        # chỉ chấp nhận các khóa nằm trong model_fields hoặc related_fields
        base = key.split('__', 1)[0]
        if base in model_fields or base in related_fields:
            if isinstance(value, list):
                filters &= Q(**{f"{key}__in": value})
            else:
                filters &= Q(**{key: value})
        else:
            # bỏ qua các tham số không hợp lệ
            continue

    # ─── 6. Queryset ───────────────────────────────────────────────────
    qs_obj = Permissions.objects.filter(filters)
    qs_obj = qs_obj.order_by(sort)

    if population:
        qs_obj = qs_obj.select_related(population)

    if fields:
        # nếu dùng values để trả về dict
        qs_obj = qs_obj.values(*fields)

    # ─── 7. Pagination ────────────────────────────────────────────────
    paginator = Paginator(qs_obj, page_size)
    try:
        page = paginator.page(current_page)
    except:
        return {
            "code": 4,
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": 'Page out of range',
            "data": None
        }

    return {
        "code": 0,
        "statusCode": status.HTTP_200_OK,
        "message": 'Fetch List Permissions with paginate',
        "currentPage": current_page,
        "pageSize": page_size,
        "totalPage": paginator.num_pages,
        "totalItem": paginator.count,
        "data": list(page),   # nếu dùng values() sẽ là list of dicts
    }

def find_one(id: str):
    if not Permissions.objects.filter(id=id, is_deleted=False).exists():
        return {
            "code": 4,
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Permission not found or deleted!",
        }

    permission = Permissions.objects.get(id=id)
    data = PermissionSerializers(permission).data
    return {
        "code": 0,
        "message": "Fetch List Permission with paginate----",
        "data": data
    }