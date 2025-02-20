from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Transaction, TransactionItem
import json

class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'
    ordering = ['-timestamp']

@require_http_methods(["POST"])
def create_transaction(request):
    data = json.loads(request.body)
    transaction = Transaction.objects.create(
        total=data['total'],
        status='pending',
        payment_method=data['payment_method']
    )
    
    for item in data['items']:
        TransactionItem.objects.create(
            transaction=transaction,
            name=item['name'],
            quantity=item['quantity'],
            price=item['price']
        )
    
    return JsonResponse({'status': 'success', 'id': transaction.id})
