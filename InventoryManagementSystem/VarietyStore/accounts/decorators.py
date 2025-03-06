from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.role:
            messages.error(request, "Access denied. User profile or role not found.")
            return redirect('inventory:product_list')
            
        if request.user.profile.role.name != "Admin":
            messages.error(request, "Access denied. Admin privileges required.")
            raise PermissionDenied("You don't have permission to perform this action.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def inventory_manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.role:
            messages.error(request, "Access denied. User profile or role not found.")
            return redirect('inventory:product_list')
            
        if request.user.profile.role.name not in ["Admin", "Inventory Manager"]:
            messages.error(request, "Access denied. Inventory management privileges required.")
            raise PermissionDenied("You don't have permission to perform this action.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
