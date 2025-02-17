from django.shortcuts import render, redirect
from .models import Product, Order
from .forms import OrderForm

def home(request):
    products = Product.objects.all()
    return render(request, 'payments/home.html', {'products': products})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = order.quantity * order.product.price
            order.payment_status = 'Pending'
            order.save()
            return redirect('process_payment', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'payments/create_order.html', {'form': form})

def process_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        order.payment_status = 'Paid'
        order.save()
        return redirect('home')
    return render(request, 'payments/process_payment.html', {'order': order})
