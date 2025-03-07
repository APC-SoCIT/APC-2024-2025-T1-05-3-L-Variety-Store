from django.urls import path
from . import views
from Sales import views as sales_views
from .views import customer_login, customer_register, customer_logout

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', customer_register, name='customer_register'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', customer_login, name='customer_login'),
    path('shop/', views.shop, name='shop'),
    path('category/<str:category>/', views.category_products, name='category_products'),
    path('logout/', customer_logout, name='customer_logout'),
]