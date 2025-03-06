from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Role
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates UserProfiles for users that do not have them'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Ensure Customer role exists
                customer_role, _ = Role.objects.get_or_create(
                    name="Customer",
                    defaults={'description': 'Default customer role'}
                )

                # Get all users without profiles
                users_without_profiles = User.objects.filter(profile__isnull=True)
                profiles_created = 0

                for user in users_without_profiles:
                    UserProfile.objects.create(
                        user=user,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        role=customer_role
                    )
                    profiles_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {profiles_created} user profiles'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating user profiles: {str(e)}'
                )
            )