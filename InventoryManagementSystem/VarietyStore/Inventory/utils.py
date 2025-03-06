from django.utils import timezone
from .models import InventoryTransaction, WeeklyReport
from decimal import Decimal
from collections import defaultdict

def generate_weekly_report():
    today = timezone.now().date()
    start_date = today - timezone.timedelta(days=today.weekday() + 7)  # Start of last week
    end_date = start_date + timezone.timedelta(days=6)  # End of last week

    transactions = InventoryTransaction.objects.filter(date__range=[start_date, end_date])

    total_earnings = Decimal('0.00')
    total_losses = Decimal('0.00')
    transaction_summary = defaultdict(lambda: {
        'quantity': 0,
        'cost': Decimal('0.00'),
        'revenue': Decimal('0.00')
    })

    for transaction in transactions:
        quantity = abs(Decimal(str(transaction.quantity)))  # Convert to positive for calculations
        cost = transaction.cost_at_transaction * quantity
        price = transaction.price_at_transaction * quantity

        # Track transaction details by type
        transaction_summary[transaction.transaction_type]['quantity'] += quantity
        transaction_summary[transaction.transaction_type]['cost'] += cost

        if transaction.transaction_type == 'sale':
            total_earnings += price
            total_losses += cost
            transaction_summary[transaction.transaction_type]['revenue'] += price
        elif transaction.transaction_type in ['ADD', 'restock']:
            total_losses += cost  # Cost of new inventory
        elif transaction.transaction_type == 'REMOVE':
            total_losses += cost  # Lost inventory value

    # Create a new report
    report = WeeklyReport.objects.create(
        start_date=start_date,
        end_date=end_date,
        total_earnings=total_earnings,
        total_losses=total_losses,
        total_profit_or_loss=total_earnings - total_losses
    )

    # Add transaction summary to report notes
    summary_notes = []
    for t_type, data in transaction_summary.items():
        summary_notes.append(
            f"{t_type}: {data['quantity']} items, "
            f"Cost: ₱{data['cost']:.2f}, "
            f"Revenue: ₱{data.get('revenue', Decimal('0.00')):.2f}"
        )

    report.notes = "\n".join(summary_notes)
    report.save()

    return report