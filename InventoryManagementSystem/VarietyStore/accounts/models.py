from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission



class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True)  # Link permissions to roles

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"
    name = models.CharField(max_length=100)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True)  # Link permissions to roles

    def __str__(self):
        return self.name
    

class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['date_joined']    
    
from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/inventory/') and hasattr(request.user, 'employee'):
            if request.user.employee.role.name not in ['Manager', 'Inventory Staff']:
                return redirect('accounts:access_denied')  # Redirect to an access denied page
        return self.get_response(request)  