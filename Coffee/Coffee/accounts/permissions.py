# accounts/permissions.py
from functools import wraps
from django.core.exceptions import PermissionDenied

def owner_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, "role", "") != "owner":
            raise PermissionDenied("Owner only")
        return view_func(request, *args, **kwargs)
    return _wrapped
