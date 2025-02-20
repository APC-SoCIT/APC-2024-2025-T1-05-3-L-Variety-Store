from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('cart/', views.cart, name='cart'),
    path('payment/', views.payment, name='payment'),
    path('receipt/', views.receipt, name='receipt'),
]