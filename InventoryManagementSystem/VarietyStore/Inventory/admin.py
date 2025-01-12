from django.contrib import admin
from .models import Employee, Supplier, Product
from django.shortcuts import render
from .models import Product

# Register your models here.

admin.site.register(Employee)
admin.site.register(Supplier)
admin.site.register(Product)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})
