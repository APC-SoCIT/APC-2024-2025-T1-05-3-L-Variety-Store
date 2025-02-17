from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_order/', views.create_order, name='create_order'),
    path('process_payment/<int:order_id>/', views.process_payment, name='process_payment'),
]
