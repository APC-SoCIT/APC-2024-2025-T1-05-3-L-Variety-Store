from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Transaction
from authentication.forms import PaymentForm

def catalog(request):
    products = Product.objects.all()
    return render(request, 'pos/catalog.html', {'products': products})

@login_required
def cart(request):
    cart_items = request.session.get('cart', {})
    return render(request, 'pos/cart.html', {'cart_items': cart_items})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session['cart'] = cart
    return redirect('catalog')
# Remove
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Process payment logic here
            transaction = Transaction.objects.create(
                user=request.user,
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method']
            )
            # Clear the cart after successful payment
            request.session['cart'] = {}
            return redirect('receipt', transaction_id=transaction.id)
    else:
        form = PaymentForm()
    return render(request, 'pos/payment.html', {'form': form})

@login_required
def receipt(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, 'pos/receipt.html', {'transaction': transaction})
