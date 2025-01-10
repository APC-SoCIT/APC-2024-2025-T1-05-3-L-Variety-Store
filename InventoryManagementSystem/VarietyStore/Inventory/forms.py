from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['ProjectName', 'ProductDescription', 'ProductQuantity', 'ProductType', 'ProductPrice']
