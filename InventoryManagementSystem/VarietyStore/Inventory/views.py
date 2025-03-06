from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Supplier, InventoryTransaction, TRANSACTION_TYPE_CHOICES, WeeklyReport
from .forms import ProductForm, SupplierForm, AdjustStockForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from accounts.models import UserProfile  # Ensure this import is correct
from django.http import JsonResponse
from .utils import generate_weekly_report  # Import the function here
from accounts.decorators import admin_required, inventory_manager_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

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
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query) |
            Q(product_barcode__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(product_category=category)
    
    # Sort functionality
    sort_by = request.GET.get('sort_by', '')
    if sort_by:
        if sort_by == 'name_asc':
            products = products.order_by('product_name')
        elif sort_by == 'name_desc':
            products = products.order_by('-product_name')
        elif sort_by == 'price_asc':
            products = products.order_by('product_price')
        elif sort_by == 'price_desc':
            products = products.order_by('-product_price')
        elif sort_by == 'quantity_asc':
            products = products.order_by('product_quantity')
        elif sort_by == 'quantity_desc':
            products = products.order_by('-product_quantity')

    context = {
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'current_category': category,
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'Inventory/product_list.html', context)

@login_required
@inventory_manager_required
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

            # Get or create UserProfile for the current user
            user_profile = UserProfile.objects.get(user=request.user)

            if product_id:  # Editing existing product
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
                        user_profile=user_profile
                    )
                    product.adjust_quantity(quantity_difference)  # Adjust product quantity accordingly
            else:  # New product
                product.save()  # Save first to get the product ID
                
                # Create an ADD transaction for the initial quantity if greater than 0
                if new_quantity > 0:
                    InventoryTransaction.objects.create(
                        product=product,
                        quantity=new_quantity,
                        transaction_type='ADD',
                        user_profile=user_profile,
                        notes=f"Initial stock for new product added by {user_profile.user.username}"
                    )

            product.save()  # Save the instance
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
@inventory_manager_required
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
@inventory_manager_required
def supplier_list(request):
    search_query = request.GET.get('search', '')
    suppliers = Supplier.objects.all()

    if search_query:
        suppliers = suppliers.filter(first_name__icontains=search_query) | suppliers.filter(last_name__icontains=search_query)

    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
@inventory_manager_required
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
@admin_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/delete_supplier.html', {'supplier': supplier})

@login_required
@inventory_manager_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, SupplierId=supplier_id)
    return render(request, 'inventory/supplier_detail.html', {'supplier': supplier})

@login_required
@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if there are any transactions for this product
    has_transactions = InventoryTransaction.objects.filter(product=product).exists()
    
    if request.method == 'POST':
        try:
            product_name = product.product_name
            product.delete()
            messages.success(request, f'Product "{product_name}" has been deleted successfully.')
            return redirect('inventory:product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('inventory:product_list')
    
    return render(request, 'Inventory/delete_product_confirm.html', {
        'product': product,
        'has_transactions': has_transactions
    })

@login_required
@inventory_manager_required
def product_status_view(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def product_gallery(request):
    products = Product.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_description__icontains=search_query) |
            Q(product_barcode__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(product_category=category)
    
    # Sort functionality
    sort_by = request.GET.get('sort_by', '')
    if sort_by:
        if sort_by == 'name_asc':
            products = products.order_by('product_name')
        elif sort_by == 'name_desc':
            products = products.order_by('-product_name')
        elif sort_by == 'price_asc':
            products = products.order_by('product_price')
        elif sort_by == 'price_desc':
            products = products.order_by('-product_price')
        elif sort_by == 'quantity_asc':
            products = products.order_by('product_quantity')
        elif sort_by == 'quantity_desc':
            products = products.order_by('-product_quantity')

    # Group products by category for gallery view
    categories = Product.CATEGORY_CHOICES
    categorized_products = {category[0]: [] for category in categories}
    
    for product in products:
        categorized_products[product.product_category].append(product)

    context = {
        'categorized_products': categorized_products,
        'categories': categories,
        'current_category': category,
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'Inventory/product_gallery.html', context)

@login_required
@inventory_manager_required
def adjust_stock(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('new_stock', 0))
            transaction_type = request.POST.get('transaction_type')

            # Validate inputs
            if quantity <= 0:
                return JsonResponse({'error': 'Quantity must be greater than 0.'}, status=400)
            
            if not transaction_type:
                return JsonResponse({'error': 'Transaction type is required.'}, status=400)
            
            if transaction_type not in ['ADD', 'REMOVE']:
                return JsonResponse({'error': 'Invalid transaction type.'}, status=400)

            # Check if removing stock would result in negative quantity
            if transaction_type == 'REMOVE' and product.product_quantity < quantity:
                return JsonResponse({'error': 'Not enough stock available.'}, status=400)

            # Get or create UserProfile for the current user
            user_profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name
                }
            )

            # Create the transaction
            transaction = InventoryTransaction.objects.create(
                product=product,
                quantity=quantity if transaction_type == "ADD" else -quantity,
                transaction_type=transaction_type,
                user_profile=user_profile
            )

            # Update product quantity
            if transaction_type == 'ADD':
                product.product_quantity += quantity
            else:  # REMOVE
                product.product_quantity -= quantity
            product.save()

            return JsonResponse({
                'success': True,
                'message': 'Stock adjusted successfully.',
                'new_quantity': product.product_quantity
            })

        except ValueError as e:
            return JsonResponse({'error': 'Invalid quantity value.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
@inventory_manager_required
def inventory_transaction_report(request):
    transaction_type = request.GET.get('transaction_type', '')
    transactions = InventoryTransaction.objects.select_related(
        'product', 
        'user_profile', 
        'user_profile__user'
    ).order_by('-date')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    return render(request, 'Inventory/inventory_transaction_report.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'transaction_type_choices': TRANSACTION_TYPE_CHOICES,
    })

@login_required
@inventory_manager_required
def weekly_report_view(request):
    reports = WeeklyReport.objects.all().order_by('-start_date')
    total_cost_price = sum(report.total_losses for report in reports)  # Calculate total cost price
    return render(request, 'Inventory/weekly_report.html', {
        'reports': reports,
        'total_cost_price': total_cost_price,  # Pass total cost price to the template
    })

@login_required
@inventory_manager_required
def generate_weekly_report_view(request):
    try:
        # Get the user's profile
        user_profile = request.user.profile

        # Generate the report and associate it with the user
        report = generate_weekly_report()
        report.generated_by = user_profile
        report.save()

        messages.success(request, "Weekly report generated successfully.")
    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
    
    return redirect('inventory:weekly_report')