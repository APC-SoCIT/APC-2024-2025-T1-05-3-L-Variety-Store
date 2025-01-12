import barcode
from barcode.writer import ImageWriter
from django.db import models
from django.conf import settings
import os
import random
import string
from django.core.files.base import ContentFile
from io import BytesIO

# Employee List Model
class Employee(models.Model):
    EmployeeId = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    Email = models.EmailField()
    Username = models.CharField(max_length=100)
    PasswordHash = models.CharField(max_length=200)
    HireDate = models.DateTimeField(auto_now_add=True)
    Role = models.CharField(max_length=100)
    AdminRoleConfiguration = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.FirstName} {self.LastName}'

# Supplier Information Model
class Supplier(models.Model):
    SupplierId = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    Email = models.EmailField()
    Phone = models.CharField(max_length=15)
    Address = models.TextField(max_length=255)
    Description = models.TextField(max_length=255)

    def __str__(self):
        return f'{self.FirstName} {self.LastName}'

# Inventory Model
class Product(models.Model):
    ProductId = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=200)
    ProductDescription = models.TextField()
    ProductQuantity = models.PositiveIntegerField()
    ProductType = models.CharField(max_length=100)
    ProductPrice = models.DecimalField(max_digits=10, decimal_places=2)
    ProductBarcode = models.CharField(max_length=50, unique=True, blank=True)
    BarcodeImage = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    ProductImage = models.ImageField(upload_to='product_images/', blank=True, null=True)
    Suppliers = models.ManyToManyField('Supplier', blank=True)

    def __str__(self):
        return self.ProductName

    def generate_unique_barcode(self):
        """Generate a unique 12-digit barcode."""
        while True:
            barcode_value = ''.join(random.choices(string.digits, k=12))
            if not Product.objects.filter(ProductBarcode=barcode_value).exists():
                return barcode_value

    def create_barcode_image(self, barcode_value):
        """Generate a barcode image in memory."""
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_value, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer)
        return buffer.getvalue()

    def save(self, *args, **kwargs):
        """Override save method to generate barcode and image."""
        # Generate barcode if not already set
        if not self.ProductBarcode:
            self.ProductBarcode = self.generate_unique_barcode()

        # Generate barcode image if not already set or file doesn't exist
        if not self.BarcodeImage or not os.path.exists(os.path.join(settings.MEDIA_ROOT, self.BarcodeImage.name)):
            barcode_image = self.create_barcode_image(self.ProductBarcode)
            image_name = f'barcodes/{self.ProductBarcode}.png'
            self.BarcodeImage.save(image_name, ContentFile(barcode_image), save=False)

        # Call the parent save method
        super().save(*args, **kwargs)

