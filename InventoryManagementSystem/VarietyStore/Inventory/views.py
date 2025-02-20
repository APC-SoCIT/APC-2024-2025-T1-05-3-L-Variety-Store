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
    products = Product.objects.all().values(
        'product_id',
        'product_name',
        'product_description',
        'product_quantity',
        'product_price',
        'product_category',
        'product_status',
        'product_barcode'
    )
    return render(request, 'Inventory/product_list.html', {'products': products})

@login_required
def product_create_or_edit(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    
    suppliers = Supplier.objects.all()
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
        suppliers = suppliers.filter(first_name__icontains=search_query) | suppliers.filter(last_name__icontains=search_query)

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

@login_required
def product_gallery(request):
    # Use select_related to get all related fields efficiently
    products = Product.objects.all()
    return render(request, 'Inventory/product_gallery.html', {'products': products})