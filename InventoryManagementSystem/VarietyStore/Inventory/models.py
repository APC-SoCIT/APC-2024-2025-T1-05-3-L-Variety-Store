from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.conf import settings
from django.utils.crypto import get_random_string
import uuid
from django.contrib.auth.models import User
from accounts.models import UserProfile  # Import UserProfile
from django.utils import timezone


# Supplier Information Model
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=255)
    description = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Inventory Model
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Pork', 'Pork'),
        ('Chicken', 'Chicken'),
        ('Beef', 'Beef'),
        ('Seafood', 'Seafood'),
        ('Ready To Cook', 'Ready To Cook'),
        ('Eggs', 'Eggs'),
        ('Others', 'Others'),
    ]
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField()
    product_quantity = models.PositiveIntegerField()
    product_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Others')
    product_status = models.BooleanField(default=False)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cost price
    product_barcode = models.CharField(max_length=50, unique=True, blank=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    suppliers = models.ManyToManyField('Supplier', related_name='products', blank=True)
    
    

    def generate_barcode(self):
        """
        Generate a unique barcode for the product and store it as a Code128 barcode.
        """
        barcode_number = get_random_string(length=12, allowed_chars='0123456789')
        
        # Ensure barcode is unique
        while Product.objects.filter(product_barcode=barcode_number).exists():
            barcode_number = get_random_string(length=12, allowed_chars='0123456789')

        self.product_barcode = barcode_number

        # Generate barcode image using the 'code128' format
        code = barcode.get_barcode_class('code128')  # Switch to 'code128'
        barcode_instance = code(barcode_number, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer)

        # Save the barcode image to the product model
        file_name = f"barcode_{barcode_number}.png"
        content = ContentFile(buffer.getvalue())
        self.barcode_image.save(file_name, content)  # Save barcode image in barcode_image field

    def save(self, *args, **kwargs):
        if not self.product_barcode:
            self.generate_barcode()  # Generate the barcode before saving
        super().save(*args, **kwargs)

    def adjust_quantity(self, quantity):
        self.product_quantity += quantity
        self.save()

    def __str__(self):
        return self.product_name

# INVENTORY TRANSACTION MODEL
TRANSACTION_TYPE_CHOICES = [
    ('sale', 'Sale'),
    ('restock', 'Restock'),
    ('adjustment', 'Adjustment'),
    ('ADD', 'Add'),  # New type for adding stock
    ('REMOVE', 'Remove'),  # New type for removing stock
]
class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()  # negative numbers for sales, positive for restock
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')  # Ensure this is correct

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.adjust_quantity(self.quantity)

    def __str__(self):
        return f"{self.transaction_type} of {self.product} ({self.quantity}) on {self.date} by {self.user_profile.user.username if self.user_profile else 'Unknown'}"

class WeeklyReport(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_losses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_profit_or_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report from {self.start_date} to {self.end_date}"