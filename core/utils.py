from django.db.models import QuerySet

def get_sort_params(request, default_sort: str = 'created', default_dir: str = 'desc'):
    """
    Extract sort parameters from request.
    Returns (sort_field, sort_direction)
    """
    sort_field = request.GET.get('sort', default_sort)
    sort_dir = request.GET.get('dir', default_dir)
    return sort_field, sort_dir

def apply_sorting(queryset: QuerySet, request, allowed_fields: list, default_sort: str = 'created', default_dir: str = 'desc'):
    """
    Apply sorting to a queryset based on request parameters.
    safely handling allowed fields.
    """
    sort_field, sort_dir = get_sort_params(request, default_sort, default_dir)
    
    if sort_field not in allowed_fields:
        sort_field = default_sort
        
    prefix = "-" if sort_dir == 'desc' else ""
    return queryset.order_by(f"{prefix}{sort_field}"), sort_field, sort_dir
