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
        ('Beverages', 'Beverages'),
        ('Bread/Bakery', 'Bread/Bakery'),
        ('Canned Goods', 'Canned Goods'),
        ('Dairy', 'Dairy'),
        ('Dry Goods', 'Dry Goods'),
        ('Meat', 'Meat'),
        ('Produce', 'Produce'),
        ('Snacks', 'Snacks'),
        ('Others', 'Others'),
    ]

    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField()
    product_quantity = models.PositiveIntegerField()
    product_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Others')
    product_status = models.BooleanField(default=False)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
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

    def __str__(self):
        return self.product_name



