from django.contrib import admin
from .models import Supplier, Product
from django.shortcuts import render
from .models import Product

# Register your models here.


admin.site.register(Supplier)
admin.site.register(Product)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active')  # Display the active status in the admin list view
    list_filter = ('active',)  # Add a filter for the active status
    search_fields = ('name',)