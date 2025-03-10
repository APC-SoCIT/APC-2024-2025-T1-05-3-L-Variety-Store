# Generated by Django 5.1.6 on 2025-03-07 01:29

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0013_alter_inventorytransaction_options_and_more'),
        ('Sales', '0004_sale_saleitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='added_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_carts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_items', to='Sales.cart'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_cart_items', to='Inventory.product'),
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'product')},
        ),
    ]
