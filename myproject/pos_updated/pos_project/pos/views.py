from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product

class POSView(TemplateView):
    template_name = 'pos/pos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meat_products'] = Product.objects.filter(category='meat')
        context['vegetable_products'] = Product.objects.filter(category='vegetable')
        return context
