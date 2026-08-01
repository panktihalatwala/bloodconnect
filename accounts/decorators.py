from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied
            profile = request.user.profile
            has_role = any(getattr(profile, f'is_{role}', False) for role in allowed_roles)
            if not has_role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator