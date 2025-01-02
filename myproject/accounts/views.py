import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserCreationFormWithRole  # Import from your own forms.py

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to a page after successful login
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to a page after successful logout

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationFormWithRole(request.POST)
        if form.is_valid():
            form.save()  # Saves the user and assigns them to the 'Customer' group
            messages.success(request, 'Your account has been created successfully.')
            time.sleep(3)
            return redirect('accounts:login')  # Redirect to the login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationFormWithRole()

    return render(request, 'accounts/register.html', {'form': form})
