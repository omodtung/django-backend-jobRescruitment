from django.db.models import Q
from django.core.paginator import Paginator
from django.apps import apps
from rest_framework import status
from .models import Companies
from .serializers import CompaniesSerializer
from utils.CheckUtils import check_permission
import re

def find_all(qs):
    """
    qs: QueryDict (ví dụ request.GET) hoặc dict chứa các tham số:
        - current, pageSize, sort, populate, fields, và các bộ lọc khác
    """
    Companies = apps.get_model('companies', 'Companies')
    model_fields = {f.name for f in Companies._meta.fields}
    related_fields = {rel.get_accessor_name() for rel in Companies._meta.related_objects}

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
                if root in related_fields and sub in {field.name for field in Companies._meta.get_field(root).related_model._meta.fields}:
                    fields.append(f)
            elif f in model_fields:
                fields.append(f)

    # ─── 5. Build filters ───────────────────────────────────────────────
    filters = Q(isDeleted=False)
    regex_pattern = re.compile(r'^/(.*)/([iI]*)$')
    for key, value in params.items():
        base = key.split('__', 1)[0]
        # chỉ chấp nhận những khóa thuộc model hoặc related
        if base in model_fields or base in related_fields:
            # nếu value là string và match regex syntax /pattern/flags
            if isinstance(value, str):
                m = regex_pattern.match(value)
                if m and key == 'name':
                    pattern, flags = m.groups()
                    if 'i' in flags.lower():
                        filters &= Q(**{f"{key}__iregex": pattern})
                    else:
                        filters &= Q(**{f"{key}__regex": pattern})
                    continue

            # xử lý list hoặc bình thường
            if isinstance(value, list):
                filters &= Q(**{f"{key}__in": value})
            else:
                filters &= Q(**{key: value})

    # ─── 6. Queryset ───────────────────────────────────────────────────
    qs_obj = Companies.objects.filter(filters)
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
        "message": 'Fetch List Companies with paginate',
        "currentPage": current_page,
        "pageSize": page_size,
        "totalPage": paginator.num_pages,
        "totalItem": paginator.count,
        "data": list(page),   # nếu dùng values() sẽ là list of dicts
    }

def find_one(id: str):
    if not Companies.objects.filter(id=id, is_deleted=False).exists():
        return {
            "code": 4,
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Companies not found or deleted!",
        }

    role = Companies.objects.get(id=id)
    data = CompaniesSerializer(role).data
    return {
        "code": 0,
        "message": "Fetch List Role with paginate----",
        "data": data
    }
