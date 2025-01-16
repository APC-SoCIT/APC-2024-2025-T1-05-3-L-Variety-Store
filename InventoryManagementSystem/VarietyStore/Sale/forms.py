from django import forms
from .models import Order, Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['OrderType', 'Discount', 'ShippingAddress']  # Modify fields as needed

    # Custom field for Barcode input
    Barcode = forms.CharField(max_length=13, required=True)

    def clean_Barcode(self):
        barcode = self.cleaned_data.get('Barcode')
        try:
            product = Product.objects.get(Barcode=barcode)
        except Product.DoesNotExist:
            raise forms.ValidationError("Product with this barcode does not exist.")
        return product
