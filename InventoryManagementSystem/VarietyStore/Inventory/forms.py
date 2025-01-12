from django import forms
from .models import Product, Supplier

class ProductForm(forms.ModelForm):
    Suppliers = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,  # Allow no suppliers
        label="Suppliers"
    )

    class Meta:
        model = Product
        fields = [
            'ProductName',
            'ProductDescription',
            'ProductQuantity',
            'ProductType',
            'ProductPrice',
            'BarcodeImage',
            'ProductImage',
            'Suppliers',
            'ProductBarcode',
        ]

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['FirstName', 'LastName', 'Email', 'Phone', 'Address', 'Description']