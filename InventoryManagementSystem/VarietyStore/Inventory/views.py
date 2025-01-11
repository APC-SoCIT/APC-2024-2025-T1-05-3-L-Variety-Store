from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm, SupplierForm
from .models import Supplier
from django.contrib import messages
from django.db.models import ObjectDoesNotExist


# Create your views here.

# List products
def product_list(request):
    products = Product.objects.prefetch_related('Suppliers')  # Optimize query for suppliers
    return render(request, 'inventory/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Save the product details
            product.save()  # Save the product instance

            # Handle suppliers
            supplier_ids = request.POST.getlist('Suppliers')  # Retrieve selected suppliers
            if supplier_ids and any(supplier_ids):  # Check if at least one supplier is selected
                valid_suppliers = Supplier.objects.filter(SupplierId__in=supplier_ids)
                product.Suppliers.set(valid_suppliers)  # Update suppliers
            else:
                product.Suppliers.clear()  # Clear suppliers if "No Supplier" is selected

            # Redirect after saving
            messages.success(request, f"Product '{product.ProjectName}' created successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()

    suppliers = Supplier.objects.all()
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'suppliers': suppliers,
        'product_form_title': 'Add Product',
    })





def product_edit(request, ProductId):
    product = get_object_or_404(Product, ProductId=ProductId)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)  # Save the product details
            product.save()  # Save the product instance

            # Handle suppliers
            supplier_ids = request.POST.getlist('Suppliers')  # Retrieve selected suppliers
            if supplier_ids and any(supplier_ids):  # Check if at least one supplier is selected
                valid_suppliers = Supplier.objects.filter(SupplierId__in=supplier_ids)
                product.Suppliers.set(valid_suppliers)  # Update suppliers
            else:
                product.Suppliers.clear()  # Clear suppliers if "No Supplier" is selected

            # Redirect after saving
            messages.success(request, f"Product '{product.ProjectName}' updated successfully.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    suppliers = Supplier.objects.all()
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'suppliers': suppliers,
        'product': product,
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
    product_name = product.ProjectName  # Capture the product name for confirmation message
    product.delete()
    messages.success(request, f'Product "{product_name}" has been successfully deleted.')
    return redirect('product_list')  # Replace 'product_list' with the name of your product list view
