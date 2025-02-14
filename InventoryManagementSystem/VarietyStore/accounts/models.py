from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


# Role Model linked to Django Groups
class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(default="No description provided")  # Set a default description
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name

# Extending User with UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.role:
            self.role = Role.objects.filter(name="Customer").first()  # Default to 'Customer' role
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"
