from django.db import models

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
    ProjectName = models.CharField(max_length=200)
    ProductDescription = models.TextField()
    ProductQuantity = models.PositiveIntegerField()
    ProductType = models.CharField(max_length=100)
    ProductPrice = models.DecimalField(max_digits=10, decimal_places=2)
    ProductBarcode = models.CharField(max_length=50)

    def __str__(self):
        return self.ProjectName