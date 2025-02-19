from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('receipt/<int:sale_id>/', views.receipt_view, name='receipt'),
]
