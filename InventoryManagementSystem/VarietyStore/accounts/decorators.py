from django.http import HttpResponseForbidden

def user_has_role(required_role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'employee') and request.user.employee.role.name == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this resource.")
        return _wrapped_view
    return decorator
