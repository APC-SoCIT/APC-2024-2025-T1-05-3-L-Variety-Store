# Generated by Django 5.1.6 on 2025-02-21 02:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0002_cart_cartitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InventoryTransaction',
        ),
    ]
