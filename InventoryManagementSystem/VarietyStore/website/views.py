from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from Inventory.models import Product, InventoryTransaction  # Import the InventoryTransaction model
from Sales.models import Cart, CartItem
from django.db.models import Sum, Count
from accounts.forms import UserRegistrationForm
from accounts.models import Role, UserProfile
import json

@login_required
def home(request):
    # Get only 4 featured products
    products = Product.objects.filter(
        product_status=True, 
        product_quantity__gt=0
    ).order_by('-product_id')[:4]  # Get latest 4 products
    
    # Get category counts for the shop section
    categories = Product.objects.filter(
        product_status=True,
        product_quantity__gt=0
    ).values('product_category').annotate(
        count=Count('product_id')
    )
    
    category_data = []
    for cat in categories:
        if cat['product_category']:  # Skip if category is None
            category_data.append({
                'name': cat['product_category'],
                'count': cat['count']
            })
    
    return render(request, 'website/home.html', {
        'products': products,
        'categories': category_data
    })

def customer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('website:home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'website/login.html')

def customer_register(request):
    if request.method == 'POST':
        # Handle registration logic here
        pass  # Implement registration logic
    return render(request, 'website/register.html')

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            product = get_object_or_404(Product, product_id=product_id)
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True
            )
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Update cart badge count
            total_items = cart.get_total_items()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Added to cart successfully',
                'cart_total': total_items
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        cart_item = get_object_or_404(CartItem, cart=cart, product__product_id=product_id)
        cart_item.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Item removed from cart',
            'cart_total': cart.get_total_items()
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        is_active=True
    )
    return render(request, 'website/cart.html', {'cart': cart})

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity')
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            
            if quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                cart_item.quantity = quantity
                cart_item.save()
                message = 'Cart updated successfully'
            
            cart = cart_item.cart
            return JsonResponse({
                'status': 'success',
                'message': message,
                'cart_total': cart.get_total_price(),
                'item_total': cart_item.get_total() if quantity > 0 else 0
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def shop(request):
    products = Product.objects.filter(product_status=True, product_quantity__gt=0)
    
    # Get category counts
    categories = Product.objects.filter(
        product_status=True,
        product_quantity__gt=0
    ).values('product_category').annotate(
        count=Count('product_id')
    )
    
    category_data = []
    for cat in categories:
        if cat['product_category']:
            category_data.append({
                'name': cat['product_category'],
                'count': cat['count']
            })
    
    return render(request, 'website/shop.html', {
        'products': products,
        'categories': category_data
    })

@login_required
def cart_count(request):
    try:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        count = cart.get_total_items() if cart else 0
        return JsonResponse({'count': count})
    except Exception as e:
        return JsonResponse({'count': 0})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    return render(request, 'website/checkout.html', {'cart': cart})

@login_required
def category_products(request, category):
    products = Product.objects.filter(
        product_status=True,
        product_quantity__gt=0,
        product_category=category
    )
    
    # Get all categories for the navigation
    categories = Product.objects.filter(
        product_status=True,
        product_quantity__gt=0
    ).values('product_category').annotate(
        count=Count('product_id')
    )
    
    category_data = []
    for cat in categories:
        if cat['product_category']:
            category_data.append({
                'name': cat['product_category'],
                'count': cat['count']
            })
    
    return render(request, 'website/category_products.html', {
        'products': products,
        'current_category': category,
        'categories': category_data
    })

def customer_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('website:customer_login')  # Redirect to the customer login page