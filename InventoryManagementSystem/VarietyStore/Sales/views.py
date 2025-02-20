from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Inventory.models import Product
from .models import Cart, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('website:cart')

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'website/cart.html', {'cart': cart})