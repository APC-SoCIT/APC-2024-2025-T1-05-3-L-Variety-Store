from django.db import models
from django.contrib.auth.models import Group, User
from Inventory.models import Product  # Adjust to your app structure
from django.core.exceptions import ValidationError


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Sold', 'Sold'),
    ]

    ORDER_TYPE_CHOICES = [
        ('Online', 'Online'),
        ('Onsite', 'Onsite'),
    ]

    OrderID = models.AutoField(primary_key=True)
    OrderDate = models.DateTimeField(auto_now_add=True)
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    OrderStatus = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='Pending')
    ShippingAddress = models.CharField(max_length=255, blank=True, null=True)  # Only used for Online orders
    OrderType = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='Onsite')
    Discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    CashierID = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
    # Ensure ShippingAddress is provided for Online orders
        if self.OrderType == 'Online' and not self.ShippingAddress:
            raise ValueError("Shipping Address is required for Online orders.")
    
    # Calculate the total amount from the sale items before saving
        total_amount = sum(item.total_price() for item in self.items.all()) - self.Discount
        self.TotalAmount = total_amount  # Apply discount
    
    # Do not modify `id`, let Django handle it
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f'{self.quantity} x {self.product.ProductName}'
