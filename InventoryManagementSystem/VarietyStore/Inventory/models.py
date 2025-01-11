import barcode
from barcode.writer import ImageWriter
from django.db import models
from django.conf import settings
import os
from django.utils.text import slugify
import random
import string
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile

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
barcode_storage = FileSystemStorage(location='media/barcodes')

class Product(models.Model):
    ProductId = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=200)
    ProductDescription = models.TextField()
    ProductQuantity = models.PositiveIntegerField()
    ProductType = models.CharField(max_length=100)
    ProductPrice = models.DecimalField(max_digits=10, decimal_places=2)
    ProductBarcode = models.CharField(max_length=50, unique=True, blank=True)
    BarcodeImage = models.ImageField(upload_to='barcodes/', storage=barcode_storage, blank=True)
    ProductImage = models.ImageField(upload_to='product_images/', blank=True, null=True)
    Suppliers = models.ManyToManyField('Supplier', blank=True)  # Use ManyToManyField for multiple suppliers

    def __str__(self):
        return self.ProductName

    def generate_barcode(self):
        """Generate a unique barcode and save it as an image."""
        barcode_value = self.ProductBarcode or self.generate_unique_barcode()
        barcode_image = self.create_barcode_image(barcode_value)
        self.BarcodeImage.save(f'{barcode_value}.png', ContentFile(barcode_image), save=False)

    def generate_unique_barcode(self):
        """Generate a unique barcode string."""
        # You can modify the length or format as per your requirement
        return ''.join(random.choices(string.digits, k=12))  # Generate a 12-digit random number

    def create_barcode_image(self, barcode_value):
        """Generate a barcode image."""
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_value, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer)
        return buffer.getvalue()

    def save(self, *args, **kwargs):
        """Override the save method to generate a barcode before saving."""
        if not self.ProductBarcode:
            self.ProductBarcode = self.generate_unique_barcode()
        self.generate_barcode()  # Generate barcode image
        super().save(*args, **kwargs)
