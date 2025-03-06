from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from Inventory.models import Product, InventoryTransaction  # Import the InventoryTransaction model
from Sales.models import Cart, CartItem
from django.db.models import Sum

@login_required
def home(request):
    products = Product.objects.filter(product_status=True)
    categorized_products = {}
    for product in products:
        categorized_products.setdefault(product.product_category, []).append(product)
    
    category_list = [
        {'name': 'Pork', 'image': 'website/images/pork.png'},
        {'name': 'Chicken', 'image': 'website/images/chicken.png'},
        {'name': 'Beef', 'image': 'website/images/beef.png'},
        {'name': 'Seafood', 'image': 'website/images/seafood.png'},
        {'name': 'Ready To Cook', 'image': 'website/images/ready.png'},
        {'name': 'Eggs', 'image': 'website/images/egg.png'},
        {'name': 'Others', 'image': 'website/images/bag.png'},
    ]
    for category in category_list:
        category['count'] = len(categorized_products.get(category['name'], []))
    
    context = {
        'categorized_products': categorized_products,
        'category_list': category_list,
    }
    return render(request, 'website/homepage.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1  # Increment quantity if item already exists
        cart_item.save()
        
        # Log the inventory transaction
        InventoryTransaction.objects.create(
            product=product,
            quantity=-1,  # Decrease in inventory
            transaction_type='sale'
        )
        
        return JsonResponse({'product_name': product.product_name, 'quantity': cart_item.quantity})
    return HttpResponseBadRequest("Invalid request method")

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product__product_id=product_id)
        cart_item.delete()
        
        # Log the inventory transaction
        InventoryTransaction.objects.create(
            product=cart_item.product,
            quantity=cart_item.quantity,  # Increase in inventory
            transaction_type='adjustment'
        )
        
        return JsonResponse({'success': True})
    else:
        return HttpResponseBadRequest("Invalid request method")

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'website/cart.html', {'cart': cart})

@login_required
def cart_count(request):
    cart = Cart.objects.filter(user=request.user).first()
    count = cart.items.aggregate(Sum('quantity'))['quantity__sum'] if cart else 0
    return JsonResponse({'count': count})

def login(request):
    return render(request, 'website/login.html')

@login_required
def shop(request):
    products = Product.objects.filter(product_status=True)
    return render(request, 'website/shop.html', {'products': products})