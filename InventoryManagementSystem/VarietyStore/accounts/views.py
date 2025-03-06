from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib import messages
from .models import Role, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserRegistrationForm, UserCreationForm, UserEditForm, UserProfileForm
from .models import Role, UserProfile

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
@user_passes_test(lambda u: u.is_superuser)
def manage_roles(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role_id = request.POST.get("role_id")

        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.role = role
        user_profile.save()

        return redirect('accounts:manage_roles') 

    users = User.objects.all()
    roles = Role.objects.all()
    return render(request, "accounts/manage_roles.html", {"users": users, "roles": roles})

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
    user = get_object_or_404(User, id=user_id)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)  # Ensure UserProfile exists

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save User
            profile_form.save()  # Save UserProfile
            messages.success(request, "User information updated successfully.")
            return redirect('accounts:manage_roles')
        else:
            messages.error(request, "Please correct the errors below.")

    roles = Role.objects.all()
    return render(request, 'accounts/edit_user.html', {
        'user': user,
        'roles': roles,
        'user_profile': user_profile,
        'user_form': UserEditForm(instance=user),
        'profile_form': UserProfileForm(instance=user_profile),
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = PasswordResetForm({'email': user.email})
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name='registration/password_reset_email.html'
        )
        messages.success(request, f"Password reset email sent to {user.email}.")
    return redirect('accounts:edit_user', user_id=user.id)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password_direct(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully.")
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