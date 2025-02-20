from django.contrib import admin
from .models import CustomUser  # Assuming you have a User model in models.py

admin.site.register(CustomUser)  # Register yung user model to admin site
