from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserCreationFormWithRole
from .models import Employee, Role
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
# Import from your own forms.py

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
            user = form.save()  # Save the user and assign them to the 'Customer' group
            messages.success(request, 'Your account has been created successfully.')
            login(request, user)  # Log in the user after registration
            return redirect('home')  # Redirect to home or any other page after successful registration
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationFormWithRole()

    return render(request, 'accounts/register.html', {'form': form})


# Admin check decorator
def is_admin(user):
    return user.is_staff  # Check if the user is an admin (is_staff or is_superuser)

@user_passes_test(is_admin)
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    roles = Role.objects.all()

    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        role = Role.objects.get(id=role_id)

        # Assign the role to the user (creating or updating the Employee record)
        employee, created = Employee.objects.get_or_create(user=user)
        employee.role = role
        employee.save()

        return redirect('success_url')  # Replace with the actual redirect URL

    return render(request, 'accounts/assign_role.html', {'user': user, 'roles': roles})