# admin.py
from django.contrib import admin
from .models import Employee, Role, Customers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    search_fields = ['user__username', 'role__name']

@admin.register(Customers)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'date_joined')  # Customize columns to display
    search_fields = ('first_name', 'last_name', 'email')  # Optional: add search functionality
    list_filter = ('date_joined',)  # Optional: filter customers by the date joined

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Role)
