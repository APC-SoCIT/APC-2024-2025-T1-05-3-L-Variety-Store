from collections import defaultdict
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product, Order, SaleItem
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@login_required
def create_order(request):
    # Check if the user is a cashier
    if not request.user.groups.filter(name='Cashiers').exists():
        return JsonResponse({'error': 'You do not have permission to access this feature.'})

    if request.method == 'POST':
        # Step 1: Adding products via barcode
        barcode = request.POST.get('barcode', None)
        quantity = int(request.POST.get('quantity', 1))  # Get quantity from input field
        if barcode:
            try:
                product = Product.objects.get(ProductBarcode=barcode)
                cart = request.session.get('cart', {})  # Always initialize cart as a dictionary

                # Update quantity in the cart (tally the count, not override)
                cart[product.ProductId] = cart.get(product.ProductId, 0) + quantity  # Tally the quantity
                request.session['cart'] = cart
                return JsonResponse({'message': 'Product added successfully.'})
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Invalid barcode.'})

        # Step 2: Removing products from the cart
        product_id_to_remove = request.POST.get('remove_product', None)
        if product_id_to_remove:
            try:
                cart = request.session.get('cart', {})  # Always retrieve cart as a dictionary
                product_id_to_remove = int(product_id_to_remove)
                if product_id_to_remove in cart:
                    del cart[product_id_to_remove]  # Remove product by ID
                    request.session['cart'] = cart
                    return JsonResponse({'message': 'Product removed successfully.'})
                else:
                    return JsonResponse({'error': 'Product not found in cart.'})
            except ValueError:
                return JsonResponse({'error': 'Invalid product ID to remove.'})

        # Step 3: Confirming the order and saving
        if 'confirm_order' in request.POST:
            cart = request.session.get('cart', {})  # Retrieve cart as a dictionary
            total_amount = 0
            products_in_cart = []

            # Ensure cart contains valid products
            for product_id, quantity in cart.items():  # Ensure cart is a dictionary
                try:
                    product = Product.objects.get(ProductId=product_id)  # Get Product instance by ProductId
                    products_in_cart.append({'product': product, 'quantity': quantity})
                    total_amount += product.ProductPrice * quantity  # Multiply by quantity
                except Product.DoesNotExist:
                    continue  # Handle case if product doesn't exist anymore

            if not products_in_cart:
                return JsonResponse({'error': 'Cart is empty. Please add products before confirming the order.'})

            # Create order
            order = Order.objects.create(
                TotalAmount=total_amount,
                OrderStatus='Pending',
                CashierID=request.user,  # Use the logged-in user as the cashier
            )

            # Create SaleItem instances for each product in the cart
            for item in products_in_cart:
                SaleItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],  # Use quantity from cart
                    price=item['product'].ProductPrice
                )

            request.session['cart'] = {}  # Clear the cart after the order is created
            return JsonResponse({'message': 'Order created successfully.'})

    # Display the products list and cart
    cart = request.session.get('cart', {})  # Always retrieve cart as a dictionary
    products_in_cart = []
    total_amount = 0
    for product_id, quantity in cart.items():  # Ensure cart is a dictionary
        try:
            product = Product.objects.get(ProductId=product_id)  # Use ProductId here
            products_in_cart.append({'product': product, 'quantity': quantity})
            total_amount += product.ProductPrice * quantity  # Multiply by quantity
        except Product.DoesNotExist:
            continue  # Skip if the product is no longer in the database

    return render(request, 'sale/order_form.html', {
        'products_in_cart': products_in_cart,
        'total_amount': total_amount,
    })
