# Generated by Django 5.1.6 on 2025-02-20 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0002_remove_product_product_type_product_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='suppliers',
            field=models.ManyToManyField(blank=True, related_name='products', to='Inventory.supplier'),
        ),
    ]
