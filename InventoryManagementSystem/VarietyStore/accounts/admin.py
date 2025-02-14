from django.contrib import admin
from .models import UserProfile, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")

