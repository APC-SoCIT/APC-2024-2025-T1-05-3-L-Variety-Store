from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('login', views.login, name='loginC'),
    path('cart', views.cart, name='cart'),
]
