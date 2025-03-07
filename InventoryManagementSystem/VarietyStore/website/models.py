from django.db import models
from django.contrib.auth.models import User
from Inventory.models import Product
from django.utils import timezone

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='website_carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def get_total_price(self):
        return sum(item.get_total() for item in self.website_items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.website_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='website_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='website_cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ('cart', 'product')
