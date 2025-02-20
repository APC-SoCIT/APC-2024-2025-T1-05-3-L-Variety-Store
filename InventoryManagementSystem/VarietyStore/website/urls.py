from django.urls import path
from . import views
from Sales import views as sales_views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='homepage'),
    path('login', views.login, name='login'),
    path('cart', views.cart, name='cart'),
    path('shop/', views.shop, name='shop'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart-count/', views.cart_count, name='cart_count'),
]