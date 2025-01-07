from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms

# This is the custom form that extends Django's UserCreationForm
class UserCreationFormWithRole(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']  # You can include other fields too

    def save(self, commit=True):
        user = super().save(commit=False)  # Get the user object
        if commit:
            user.save()  # Save the user to the database
        
        # Assign the new user to the 'Customer' group
        customer_group = Group.objects.get(name='Customer')
        user.groups.add(customer_group)
        
        return user
