from django.db import models
from django.conf import settings
from Inventory.models import Product  # Assuming Inventory app provides Product model
from accounts.models import UserProfile

# Sale Model for completed transactions
class Sale(models.Model):
    SALE_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='completed')
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)

    @property
    def items_count(self):
        return self.saleitems.count()

    def __str__(self):
        return f"Sale #{self.invoice_number}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='saleitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name if self.product else 'Unknown Product'}"

# ORDER MODEL
ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    # add more statuses as needed
]

ORDER_TYPE_CHOICES = [
    ('onsite', 'Onsite'),
    ('online', 'Online'),
]

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_details = models.TextField(blank=True, null=True)
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE_CHOICES)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_cashier')

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"

# DISCOUNT MODEL
DISCOUNT_TYPE_CHOICES = [
    ('percentage', 'Percentage'),
    ('fixed', 'Fixed Amount'),
]

class Discount(models.Model):
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    # You can relate a discount either to a single product...
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    # ...or you might want to relate it to a category instead.
    # category = models.CharField(max_length=100, blank=True, null=True)  # For category-wide discount

    def __str__(self):
        return f"{self.discount_type} - {self.discount_amount}"

# PAYMENT MODEL
PAYMENT_TYPE_CHOICES = [
    ('cash', 'Cash'),
    ('card', 'Card'),
    # add more types (e.g., mobile) if needed
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment #{self.pk} for Order #{self.order.pk}"


    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"