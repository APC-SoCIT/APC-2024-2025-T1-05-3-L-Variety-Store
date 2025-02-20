from django.contrib import admin
from .models import CustomUser  # Assuming you have a User model in models.py

admin.site.register(CustomUser)  # Register the User model with the admin site