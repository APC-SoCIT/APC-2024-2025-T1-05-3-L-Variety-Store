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

    for transaction in transactions:
        quantity = Decimal(transaction.quantity)

        if transaction.transaction_type == 'sale':
            total_earnings += transaction.product.product_price * quantity
            total_losses += transaction.product.cost_price * quantity
        elif transaction.transaction_type == 'restock':
            total_losses += transaction.product.cost_price * quantity

    total_profit_or_loss = total_earnings - total_losses

    # Create a new report entry without checking for existing reports
    report = WeeklyReport.objects.create(
        start_date=start_date,
        end_date=end_date,
        total_earnings=total_earnings,
        total_losses=total_losses,
        total_profit_or_loss=total_profit_or_loss
    )
    return report