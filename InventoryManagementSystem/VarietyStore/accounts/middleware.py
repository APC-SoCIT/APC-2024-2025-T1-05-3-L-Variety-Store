# accounts/middleware.py

from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/inventory/'):
            if request.user.employee.role.name not in ['Manager', 'Inventory Staff']:
                return redirect('accounts:access_denied')  # Replace with the correct view name
        return self.get_response(request)
