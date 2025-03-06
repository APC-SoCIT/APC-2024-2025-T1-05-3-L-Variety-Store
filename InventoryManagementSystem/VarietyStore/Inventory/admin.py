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
    
    
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'transaction_type', 'date', 'user_profile')  # Fields to display in the list view
    list_filter = ('transaction_type', 'date', 'user_profile')  # Filters for the admin interface
    search_fields = ('product__name', 'user_profile__user__username')  # Searchable fields

    def get_queryset(self, request):
        # Override to include related user profile information
        qs = super().get_queryset(request)
        return qs.select_related('user_profile')  # Optimize query for user profile

    def user_profile(self, obj):
        return obj.user_profile.user.username if obj.user_profile else 'Unknown'  # Display username in admin

    user_profile.short_description = 'User'  # Set column name in admin