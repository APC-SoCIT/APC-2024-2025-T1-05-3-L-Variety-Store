from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms
from .models import Role

class UserCreationFormWithRole(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']  # You can include other fields too

    def save(self, commit=True):
        user = super().save(commit=False)  # Get the user object
        if commit:
            user.save()  # Save the user to the database
        
        # Automatically assign the user to the 'Customers' group
        customer_group = Group.objects.get(name='Customers')  # Ensure 'Customers' group exists
        user.groups.add(customer_group)
        
        return user
    
from django import forms
from django.contrib.auth.models import User
from accounts.models import Employee, Role

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()

            # Assign default role (e.g., "Customer")
            default_role, _ = Role.objects.get_or_create(name="Customers")
            Employee.objects.create(user=user, role=default_role)
        return user
