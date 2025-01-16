from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.utils.crypto import get_random_string
import uuid


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
    ProductStatus =models.BooleanField(default=False)
    ProductPrice = models.DecimalField(max_digits=10, decimal_places=2)
    ProductBarcode = models.CharField(max_length=50, unique=True, blank=True)
    BarcodeImage = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    ProductImage = models.ImageField(upload_to='product_images/', blank=True, null=True)
    Suppliers = models.ManyToManyField('Supplier', blank=True)
    
    

    def generate_barcode(self):
        """
        Generate a unique barcode for the product and store it as a Code128 barcode.
        """
        barcode_number = get_random_string(length=12, allowed_chars='0123456789')
        
        # Ensure barcode is unique
        while Product.objects.filter(ProductBarcode=barcode_number).exists():
            barcode_number = get_random_string(length=12, allowed_chars='0123456789')

        self.ProductBarcode = barcode_number

        # Generate barcode image using the 'code128' format
        code = barcode.get_barcode_class('code128')  # Switch to 'code128'
        barcode_instance = code(barcode_number, writer=ImageWriter())
        buffer = BytesIO()
        barcode_instance.write(buffer)

        # Save the barcode image to the product model
        file_name = f"barcode_{barcode_number}.png"
        content = ContentFile(buffer.getvalue())
        self.BarcodeImage.save(file_name, content)  # Save barcode image in BarcodeImage field

    def save(self, *args, **kwargs):
        if not self.ProductBarcode:
            self.generate_barcode()  # Generate the barcode before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ProductName



