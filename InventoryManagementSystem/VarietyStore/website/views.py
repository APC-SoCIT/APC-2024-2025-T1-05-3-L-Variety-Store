from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'web/index.html')

def login(request):
    return render(request, 'web/login.html')

def cart(request):
    return render(request, 'web/cart.html')
