from django.contrib import admin
from .models import Product, Transaction
#ADMIN
admin.site.register(Product)
admin.site.register(Transaction)
