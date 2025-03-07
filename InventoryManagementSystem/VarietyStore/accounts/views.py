from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib import messages
from .models import Role, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserRegistrationForm, UserCreationForm, UserEditForm, UserProfileForm
from .models import Role, UserProfile
from Inventory.models import InventoryTransaction
from Sales.models import Sale
from django.db.models import Count, Sum
from accounts.decorators import admin_required
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been created successfully.")
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/signup.html', {'form': form})

def is_admin(user):
    return user.is_superuser

@login_required
@admin_required
def manage_roles(request):
    # Get all users and roles
    users = User.objects.select_related('profile__role').all()
    roles = Role.objects.all()

    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__first_name__icontains=search_query) |
            Q(profile__last_name__icontains=search_query)
        )

    # Handle role filtering
    selected_role = request.GET.get('role', '')
    if selected_role:
        users = users.filter(profile__role_id=selected_role)

    # Handle sorting
    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'username_asc':
        users = users.order_by('username')
    elif sort_by == 'username_desc':
        users = users.order_by('-username')
    elif sort_by == 'date_joined':
        users = users.order_by('-date_joined')
    else:
        users = users.order_by('username')  # Default sorting

    context = {
        'users': users,
        'roles': roles,
        'search_query': search_query,
        'selected_role': selected_role,
        'current_sort': sort_by,
    }

    return render(request, 'accounts/manage_roles.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html'
            )
            messages.success(request, f"Password reset email sent to {user.email}.")
            return redirect('accounts:manage_roles')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/reset_password.html', {'form': form, 'user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    # Get the target user being edited
    target_user = get_object_or_404(User, id=user_id)
    user_profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == "POST":
        # Store current admin's session key
        current_session_key = request.session.session_key
        
        user_form = UserEditForm(request.POST, instance=target_user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Restore admin's session
            if target_user.id != request.user.id:
                request.session.cycle_key()
            
            messages.success(request, "User information updated successfully.")
            return redirect('accounts:manage_roles')
        else:
            messages.error(request, "Please correct the errors below.")

    roles = Role.objects.all()
    return render(request, 'accounts/edit_user.html', {
        'edited_user': target_user,  # Changed from 'user' to 'edited_user'
        'roles': roles,
        'user_profile': user_profile,
        'user_form': UserEditForm(instance=target_user),
        'profile_form': UserProfileForm(instance=user_profile),
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password_direct(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        if not new_password:
            messages.error(request, "Password cannot be empty.")
            return redirect('accounts:edit_user', user_id=target_user.id)
        
        try:
            # Validate password
            validate_password(new_password, target_user)
            
            # Only manage session if we're not changing our own password
            if target_user.id != request.user.id:
                current_session_key = request.session.session_key
            
            # Set the new password for the target user
            target_user.set_password(new_password)
            target_user.save()
            
            # Restore admin's session only if we changed someone else's password
            if target_user.id != request.user.id:
                request.session.cycle_key()
            
            messages.success(request, f"Password for {target_user.username} has been changed successfully.")
        except ValidationError as e:
            messages.error(request, "\n".join(e.messages))
        except Exception as e:
            messages.error(request, f"An error occurred while changing the password: {str(e)}")
    
    return redirect('accounts:edit_user', user_id=target_user.id)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html'
            )
            messages.success(request, f"Password reset email sent to {user.email}.")
        else:
            messages.error(request, "Invalid email address.")
    except Exception as e:
        messages.error(request, f"An error occurred while sending the reset email: {str(e)}")
    
    return redirect('accounts:edit_user', user_id=user.id)

from .forms import UserCreationForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile and assign a default role
            user_profile = UserProfile.objects.create(user=user)
            default_role = Role.objects.filter(name='Customer').first()  # Adjust the role name as necessary
            if default_role:
                user_profile.role = default_role
                user_profile.save()
            messages.success(request, "New account created successfully.")
            return redirect('accounts:manage_roles')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
def user_profile(request, user_id):
    # Get the user profile
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    # Check if the user has permission to view this profile
    if request.user != user_profile.user and not request.user.profile.role.name == 'Admin':
        messages.error(request, "You don't have permission to view this profile.")
        return redirect('inventory:product_list')
    
    # Get inventory transactions
    inventory_transactions = InventoryTransaction.objects.filter(
        user_profile=user_profile
    ).select_related('product').order_by('-date')[:10]  # Get last 10 transactions
    
    inventory_transactions_count = InventoryTransaction.objects.filter(
        user_profile=user_profile
    ).count()
    
    # Get sales data
    sales = Sale.objects.filter(
        user_profile=user_profile
    ).order_by('-date')[:10]  # Get last 10 sales
    
    sales_count = Sale.objects.filter(
        user_profile=user_profile
    ).count()
    
    total_sales_amount = Sale.objects.filter(
        user_profile=user_profile,
        status='completed'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'user_profile': user_profile,
        'inventory_transactions': inventory_transactions,
        'inventory_transactions_count': inventory_transactions_count,
        'sales': sales,
        'sales_count': sales_count,
        'total_sales_amount': total_sales_amount,
    }
    
    return render(request, 'accounts/user_profile.html', context)