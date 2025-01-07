from django.urls import path
from .views import scan_barcode, storefront_view

urlpatterns = [
    path('scan/', scan_barcode, name='scan_barcode'),
    path('Storefront/', storefront_view, name='Sale'),

]
