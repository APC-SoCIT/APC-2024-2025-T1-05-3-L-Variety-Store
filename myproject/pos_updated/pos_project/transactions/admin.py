from django.contrib import admin
from .models import Transaction, TransactionItem

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'total', 'status', 'payment_method']
    inlines = [TransactionItemInline]
