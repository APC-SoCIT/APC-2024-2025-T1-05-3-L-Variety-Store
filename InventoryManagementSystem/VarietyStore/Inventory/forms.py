from django import forms
from .models import Product, Supplier

class ProductForm(forms.ModelForm):
    suppliers = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label="Suppliers"
    )

    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_description',
            'product_quantity',
            'product_category',
            'product_price',
            'cost_price',
            'barcode_image',
            'product_image',
            'suppliers',
            'product_barcode',
            'product_status',
        ]
        widgets = {
            'product_category': forms.Select(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'description']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class AdjustStockForm(forms.Form):
    ACTION_CHOICES = [
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect, label="Action")
    new_stock = forms.IntegerField(min_value=1, label="Quantity", widget=forms.NumberInput(attrs={'class': 'form-control'}))