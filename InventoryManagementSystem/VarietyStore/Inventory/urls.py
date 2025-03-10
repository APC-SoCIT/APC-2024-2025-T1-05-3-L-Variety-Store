from django.urls import path, include
from . import views

app_name = 'inventory'

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create_or_edit, name='product_create'),
    path('products/edit/<int:product_id>/', views.product_create_or_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.delete_product, name='product_delete'),
    path('supplier/create/', views.create_supplier, name='create_supplier'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
    path('supplier/update/<int:pk>/', views.update_supplier, name='update_supplier'),
    path('supplier/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),
    path('supplier/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('products/gallery/', views.product_gallery, name='product_gallery'),
    path('products/adjust_stock/<int:product_id>/', views.adjust_stock, name='adjust_stock'),
    path('inventory-transactions/', views.inventory_transaction_report, name='inventory_transaction_report'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('generate-weekly-report/', views.generate_weekly_report_view, name='generate_weekly_report'),
    path('weekly-report/', views.weekly_report_view, name='weekly_report'),
]