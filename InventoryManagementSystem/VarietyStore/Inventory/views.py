from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm, SupplierForm
from .models import Supplier
from django.contrib import messages

# Create your views here.

# List products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

# Create a new product
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})


def product_edit(request, ProductId):
    product = get_object_or_404(Product, pk=ProductId)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

# Edit a product
def product_edit(request, ProductId):
    product = get_object_or_404(Product, pk=ProductId)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})


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
