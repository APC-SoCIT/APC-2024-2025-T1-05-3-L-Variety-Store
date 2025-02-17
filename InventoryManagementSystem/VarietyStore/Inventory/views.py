from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Supplier
from .forms import ProductForm, SupplierForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal

def format_price(value, currency='PHP'):
    if value is None:
        return f'0.00 {currency}'
    
    try:
        value = Decimal(value)
    except (ValueError, TypeError):
        return f'{value} {currency}'
    
    # Currency symbols and conversion rates
    symbols = {
        'USD': '$',
        'PHP': '₱',
        'EUR': '€',
        'JPY': '¥',
        'GBP': '£',
    }
    conversion_rates = {
        'USD': Decimal('1.0'),
        'EUR': Decimal('0.85'),
        'JPY': Decimal('110.0'),
        'GBP': Decimal('0.75'),
        'PHP': Decimal('50.0'),
    }

    if currency in conversion_rates:
        converted_price = value / conversion_rates['PHP'] * conversion_rates[currency]
        currency_symbol = symbols.get(currency, currency)
        return f'{currency_symbol}{converted_price:.2f}'
    
    # Default to PHP if currency not found
    currency_symbol = symbols.get(currency, 'PHP')
    return f'{currency_symbol}{value:.2f}'

@login_required
def product_list(request):
    products = Product.objects.all()
    
    # Update active status based on stock and save changes to the database
    for product in products:
        if product.ProductQuantity == 0:  # Check stock value
            product.ProductStatus = False  # Set active status to False
            product.save()  # Save the changes to the database

    currency = request.GET.get('currency', 'PHP')
    product_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '')

    # Get only unique product types that are used by products in the database
    used_product_types = Product.objects.values_list('ProductType', flat=True).distinct()

    # Filtering by product type
    if product_type:
        products = products.filter(ProductType=product_type)

    # Search by product name
    if search_query:
        products = products.filter(ProductName__icontains=search_query)

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('ProductPrice')
    elif sort_by == 'price_desc':
        products = products.order_by('-ProductPrice')
    elif sort_by == 'stock_asc':
        products = products.order_by('ProductQuantity')
    elif sort_by == 'stock_desc':
        products = products.order_by('-ProductQuantity')
    elif sort_by == 'active':
        products = products.order_by('ProductStatus')

    # Format the products for currency and other fields
    formatted_products = []
    for product in products:
        formatted_price = format_price(product.ProductPrice, currency)
        formatted_products.append({
            'ProductId': product.ProductId,  # Ensure ProductId is included
            'image': product.ProductImage.url if product.ProductImage else None,
            'name': product.ProductName,
            'type': product.ProductType,
            'price': formatted_price,
            'barcode': product.ProductBarcode,
            'barcode_image': product.BarcodeImage.url if product.BarcodeImage else None,
            'active': product.ProductStatus,
            'suppliers': product.Suppliers.all(),
            'stock': product.ProductQuantity,
        })

    return render(request, 'inventory/product_list.html', {
        'products': formatted_products,
        'currency': currency,
        'product_types': used_product_types,  # Pass the list of used product types
    })

@login_required
def product_create_or_edit(request, ProductId=None):
    # If ProductId is provided, fetch the product for editing
    product = None
    if ProductId:
        product = get_object_or_404(Product, ProductId=ProductId)
    
    # Handle the form submission (both for creating and editing)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Pass the existing product for editing
        if form.is_valid():
            form.save()  # Save the new or updated product
            return redirect('inventory:product_list')  # Redirect to the product list after saving
    else:
        form = ProductForm(instance=product)  # Initialize the form with existing product data (if editing)
    
    # Pass all suppliers for the dropdown
    suppliers = Supplier.objects.all()

    # Set the appropriate title based on whether the product exists (edit or create)
    form_title = 'Edit Product' if product else 'Create Product'
    
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'suppliers': suppliers,
        'product': product,
        'product_form_title': form_title,
    })

@login_required
def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:supplier_list')  # Replace with the appropriate URL
    else:
        form = SupplierForm()

    return render(request, 'inventory/create_supplier.html', {'form': form})

@login_required
def supplier_list(request):
    search_query = request.GET.get('search', '')
    suppliers = Supplier.objects.all()

    if search_query:
        suppliers = suppliers.filter(FirstName__icontains=search_query) | suppliers.filter(LastName__icontains=search_query)

    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/update_supplier.html', {'form': form})

@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/delete_supplier.html', {'supplier': supplier})

@login_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, SupplierId=supplier_id)
    return render(request, 'inventory/supplier_detail.html', {'supplier': supplier})

@login_required
def delete_product(request, product_id):
    """Handle deleting a product."""
    product = get_object_or_404(Product, ProductId=product_id)
    product_name = product.ProductName  # Corrected field name
    product.delete()
    messages.success(request, f'Product "{product_name}" has been successfully deleted.')
    return redirect('inventory:product_list')

@login_required
def product_status_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})