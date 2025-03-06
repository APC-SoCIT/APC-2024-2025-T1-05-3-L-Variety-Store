from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

# Role Model linked to Django Groups
class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(default="No description provided")
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        db_table = 'accounts_role'

    def __str__(self):
        return self.name

# Extending User with UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'accounts_userprofile'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.role:
                # Try to get or create the Customer role
                self.role, _ = Role.objects.get_or_create(
                    name="Customer",
                    defaults={'description': 'Default customer role'}
                )
            
            # Set first_name and last_name from User if not set
            if not self.first_name and self.user:
                self.first_name = self.user.first_name
            if not self.last_name and self.user:
                self.last_name = self.user.last_name
                
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile when a user is created or updated.
    """
    with transaction.atomic():
        if created:
            # Ensure the Customer role exists
            customer_role, _ = Role.objects.get_or_create(
                name="Customer",
                defaults={'description': 'Default customer role'}
            )
            
            # Create new UserProfile
            UserProfile.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                role=customer_role
            )
        else:
            # Get or create the profile and update it
            profile, profile_created = UserProfile.objects.get_or_create(user=instance)
            if not profile_created:
                profile.first_name = instance.first_name
                profile.last_name = instance.last_name
                profile.save()