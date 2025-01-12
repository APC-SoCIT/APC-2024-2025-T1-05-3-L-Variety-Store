from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm, SupplierForm
from .models import Supplier
from django.contrib import messages
from django.db.models import ObjectDoesNotExist


# Create your views here.

# List products
from decimal import Decimal

# Helper function for formatting price
def format_price(price, currency='PHP'):
    conversion_rates = {
        'USD': Decimal('1.0'),
        'EUR': Decimal('0.85'),
        'JPY': Decimal('110.0'),
        'GBP': Decimal('0.75'),
        'PHP': Decimal('50.0'),
    }
    if currency in conversion_rates:
        converted_price = price / conversion_rates['PHP'] * conversion_rates[currency]  # Assuming price is in PHP
        return f'{converted_price:.2f} {currency}'
    return f'{price:.2f} PHP'

# Updated product_list view
def product_list(request):
    products = Product.objects.all()
    selected_currency = request.GET.get('currency', 'PHP')  # Default to PHP

    # Add all necessary fields
    formatted_products = []
    for product in products:
        formatted_products.append({
            'id': product.ProductId,
            'image': product.ProductImage.url if product.ProductImage else None,
            'name': product.ProductName,
            'type': product.ProductType,
            'price': format_price(product.ProductPrice, selected_currency),
            'barcode': product.ProductBarcode,
            'barcode_image': product.BarcodeImage.url if product.BarcodeImage else None,
            'suppliers': product.Suppliers.all(),
        })

    return render(request, 'inventory/product_list.html', {
        'products': formatted_products,
        'currency': selected_currency,
    })




def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Save the product instance but don't commit yet
            product.save()  # Save the product instance

            # Save the many-to-many relationship
            suppliers = request.POST.getlist('Suppliers')  # Get the list of supplier IDs
            product.Suppliers.set(suppliers)  # Set the ManyToManyField

            return redirect('product_list')  # Replace with the appropriate URL
    else:
        form = ProductForm()

    suppliers = Supplier.objects.all()  # Fetch all suppliers for dropdown options
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'suppliers': suppliers,  # Send all suppliers to the template
        'product': None,  # No product data since it's a new product
        'product_form_title': 'Create Product',
    })





def product_edit(request, ProductId):
    product = get_object_or_404(Product, ProductId=ProductId)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)  # Save the product instance but don't commit yet
            product.save()  # Save the product instance

            # Update the many-to-many relationship
            suppliers = request.POST.getlist('Suppliers')  # Get the list of supplier IDs
            product.Suppliers.set(suppliers)  # Set the ManyToManyField

            return redirect('product_list')  # Replace with the appropriate URL
    else:
        form = ProductForm(instance=product)

    suppliers = Supplier.objects.all()  # Fetch all suppliers for dropdown options
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'suppliers': suppliers,
        'product': product,  # Pass the product for existing supplier prepopulation
        'product_form_title': 'Edit Product',
    })









def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')  # Replace with the appropriate URL
    else:
        form = SupplierForm()

    return render(request, 'inventory/create_supplier.html', {'form': form})

def supplier_list(request):
    suppliers = Supplier.objects.all()  # Fetch all suppliers
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/update_supplier.html', {'form': form})
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'inventory/delete_supplier.html', {'supplier': supplier})

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, SupplierId=supplier_id)
    return render(request, 'inventory/supplier_detail.html', {'supplier': supplier})


def delete_product(request, product_id):
    """Handle deleting a product."""
    product = get_object_or_404(Product, ProductId=product_id)
    product_name = product.ProductName  # Corrected field name
    product.delete()
    messages.success(request, f'Product "{product_name}" has been successfully deleted.')
    return redirect('product_list')


