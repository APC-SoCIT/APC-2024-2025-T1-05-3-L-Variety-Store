from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.utils import OperationalError

        # Ensure groups exist after migrations
        def create_default_groups(sender, **kwargs):
            groups = ['Customers', 'Managers', 'Inventory Staff']  # Add any other groups you need
            for group_name in groups:
                try:
                    Group.objects.get_or_create(name=group_name)
                except OperationalError:
                    # Ignore if the database is not ready
                    pass

        post_migrate.connect(create_default_groups, sender=self)