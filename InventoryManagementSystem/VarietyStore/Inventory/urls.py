from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:ProductId>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:product_id>/', views.delete_product, name='product_delete'),
    path('supplier/create/', views.create_supplier, name='create_supplier'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
    path('supplier/update/<int:pk>/', views.update_supplier, name='update_supplier'),
    path('supplier/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),
    path('supplier/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
]
