from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Supplier, InventoryTransaction, TRANSACTION_TYPE_CHOICES
from .forms import ProductForm, SupplierForm, AdjustStockForm
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
    products = Product.objects.all().prefetch_related('suppliers')
    return render(request, 'Inventory/product_list.html', {'products': products})

@login_required
def product_create_or_edit(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, product_id=product_id)
        form_title = "Edit Product"
    else:
        product = None
        form_title = "Add Product"

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save M2M yet
            product.save()  # Save the instance first
            form.save_m2m()  # Now save the M2M data
            messages.success(request, "Product saved successfully.")
            return redirect('inventory:product_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)
        form_title = "Edit Product" if product_id else "Add Product"

    return render(request, 'Inventory/product_form.html', {
        'form': form,
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
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product "{product.product_name}" has been deleted.')
        return redirect('inventory:product_list')
    return render(request, 'Inventory/delete_product_confirm.html', {'product': product})

@login_required
def product_status_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def product_gallery(request):
    products = Product.objects.all()
    categories = Product.CATEGORY_CHOICES  # Get the category choices from the Product model
    categorized_products = {category[0]: [] for category in categories}  # Create a dictionary for categories

    # Group products by category
    for product in products:
        categorized_products[product.product_category].append(product)

    return render(request, 'Inventory/product_gallery.html', {'categorized_products': categorized_products})

@login_required
def adjust_stock(request, product_id):
    """Handle adjusting stock for a product."""
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        form = AdjustStockForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action')
            quantity = form.cleaned_data.get('new_stock')

            if action == 'add':
                product.product_quantity += quantity
                messages.success(request, f'Stock for "{product.product_name}" has been increased by {quantity}.')
            elif action == 'remove':
                if quantity > product.product_quantity:
                    messages.error(request, f'Cannot remove {quantity} units. Only {product.product_quantity} in stock.')
                    return redirect(request.META.get('HTTP_REFERER', 'inventory:product_list'))
                product.product_quantity -= quantity
                messages.success(request, f'Stock for "{product.product_name}" has been decreased by {quantity}.')
            else:
                messages.error(request, "Invalid action.")
                return redirect(request.META.get('HTTP_REFERER', 'inventory:product_list'))

            # Create an InventoryTransaction
            InventoryTransaction.objects.create(
                product=product,
                quantity=quantity if action == 'add' else -quantity,
                transaction_type=action,
                user=request.user
            )

            product.save()
            return redirect(request.META.get('HTTP_REFERER', 'inventory:product_list'))
        else:
            messages.error(request, "Invalid input. Please try again.")
            return redirect(request.META.get('HTTP_REFERER', 'inventory:product_list'))
    
    return redirect('inventory:product_list')

@login_required
def inventory_transaction_report(request):
    transaction_type = request.GET.get('transaction_type', '')
    transactions = InventoryTransaction.objects.all().order_by('-date')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    return render(request, 'Inventory/inventory_transaction_report.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'transaction_type_choices': TRANSACTION_TYPE_CHOICES,
    })