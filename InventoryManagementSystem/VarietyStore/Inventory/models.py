from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.utils.crypto import get_random_string

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

    def generate_barcode(self):
        """
        Generate a unique barcode for the product and store it.
        """
        barcode_number = get_random_string(length=12, allowed_chars='0123456789')
        # Ensure barcode is unique
        while Product.objects.filter(ProductBarcode=barcode_number).exists():
            barcode_number = get_random_string(length=12, allowed_chars='0123456789')

        self.ProductBarcode = barcode_number

        # Generate barcode image using the 'ean13' format or any other format
        code = barcode.get_barcode_class('ean13')
        barcode_instance = code(barcode_number, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer)

        # Save the barcode image to the product model
        file_name = f"barcode_{barcode_number}.png"
        content = ContentFile(buffer.getvalue())
        self.ProductBarcodeImage.save(file_name, content)

    def save(self, *args, **kwargs):
        if not self.ProductBarcode:  # Generate barcode if not already set
            self.generate_barcode()

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.ProductName



