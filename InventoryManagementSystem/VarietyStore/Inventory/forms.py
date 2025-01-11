from django import forms
from .models import Product, Supplier

class ProductForm(forms.ModelForm):
    Suppliers = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Product
        fields = ['ProjectName', 'ProductQuantity', 'ProductPrice', 'ProductBarcode', 'BarcodeImage', 'Suppliers']

from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['FirstName', 'LastName', 'Email', 'Phone', 'Address', 'Description']