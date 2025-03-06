from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Supplier, InventoryTransaction, TRANSACTION_TYPE_CHOICES, WeeklyReport
from .forms import ProductForm, SupplierForm, AdjustStockForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from accounts.models import UserProfile  # Ensure this import is correct
from django.http import JsonResponse
from .utils import generate_weekly_report  # Import the function here

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
        original_quantity = product.product_quantity  # Store the original quantity
        form_title = "Edit Product"
    else:
        product = None
        original_quantity = 0  # No original quantity for new products
        form_title = "Add Product"

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save M2M yet
            new_quantity = form.cleaned_data['product_quantity']  # Get the new quantity

            # Adjust stock based on the difference
            if product_id:  # Only adjust stock if editing an existing product
                quantity_difference = new_quantity - original_quantity
                if quantity_difference != 0:
                    # Check if the new quantity would be negative
                    if product.product_quantity + quantity_difference < 0:
                        messages.error(request, "Stock quantity cannot be negative.")
                        return render(request, 'Inventory/product_form.html', {
                            'form': form,
                            'product_form_title': form_title,
                        })

                    # Create an InventoryTransaction for the adjustment
                    transaction_type = 'restock' if quantity_difference > 0 else 'sale'
                    InventoryTransaction.objects.create(
                        product=product,
                        quantity=quantity_difference,
                        transaction_type=transaction_type,
                        user_profile=UserProfile.objects.get(user=request.user)  # Get the UserProfile for the logged-in user
                    )
                    product.adjust_quantity(quantity_difference)  # Adjust product quantity accordingly

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
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('new_stock', 0))  # Get the quantity from the form
        transaction_type = request.POST.get('transaction_type')  # Get the transaction type

        # Check if transaction_type is provided
        if not transaction_type:
            return JsonResponse({'error': 'Transaction type is required.'}, status=400)

        # Get the UserProfile for the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)

        # Create the InventoryTransaction instance
        InventoryTransaction.objects.create(
            product=product,
            quantity=quantity if transaction_type == "ADD" else -quantity,  # Adjust quantity based on action
            transaction_type=transaction_type,
            user_profile=user_profile  # Ensure this is correct
        )

        # Return a success response
        return JsonResponse({'success': True, 'message': 'Stock adjusted successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

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

@login_required
def weekly_report_view(request):
    reports = WeeklyReport.objects.all().order_by('-start_date')
    total_cost_price = sum(report.total_losses for report in reports)  # Calculate total cost price
    return render(request, 'Inventory/weekly_report.html', {
        'reports': reports,
        'total_cost_price': total_cost_price,  # Pass total cost price to the template
    })

@login_required
def generate_weekly_report_view(request):
    # Call the function to generate the weekly report
    generate_weekly_report()  # Assuming this function is defined in utils.py
    messages.success(request, "Weekly report generated successfully.")
    return redirect('inventory:weekly_report')  # Use the correct namespace