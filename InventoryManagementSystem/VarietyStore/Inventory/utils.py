from django.utils import timezone
from datetime import timedelta
from .models import InventoryTransaction, WeeklyReport
from django.db.models import Sum, F
from decimal import Decimal
from collections import defaultdict

def generate_weekly_report(start_date=None, end_date=None):
    """
    Generate a report for the specified date range.
    If no dates are provided, defaults to the last 7 days.
    """
    if end_date is None:
        end_date = timezone.now()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    # Get all transactions within the date range
    transactions = InventoryTransaction.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('product')  # Add select_related for better performance

    # Initialize totals
    total_earnings = Decimal('0.00')
    total_losses = Decimal('0.00')

    # Create a nested defaultdict for product-specific summaries
    product_summary = defaultdict(lambda: defaultdict(lambda: {
        'quantity': 0,
        'cost': Decimal('0.00'),
        'revenue': Decimal('0.00')
    }))

    # Process all transactions
    for transaction in transactions:
        product_name = transaction.product.product_name
        tx_type = transaction.transaction_type
        quantity = abs(transaction.quantity)
        cost = transaction.cost_at_transaction * quantity
        revenue = transaction.price_at_transaction * quantity

        # Update product summary
        product_summary[product_name][tx_type]['quantity'] += quantity
        product_summary[product_name][tx_type]['cost'] += cost
        product_summary[product_name][tx_type]['revenue'] += revenue

        # Update totals
        if tx_type == 'sale':
            total_earnings += revenue
        elif tx_type == 'REMOVE':
            total_losses += cost

    # Create detailed transaction summary notes
    summary_notes = []
    
    # Add a header
    summary_notes.append("=== Product-wise Transaction Summary ===\n")
    
    # Sort products alphabetically
    for product_name in sorted(product_summary.keys()):
        summary_notes.append(f"\nProduct: {product_name}")
        product_data = product_summary[product_name]
        
        # Show transaction types in a specific order
        for tx_type in ['sale', 'restock', 'ADD', 'REMOVE']:
            if tx_type in product_data:
                data = product_data[tx_type]
                summary_notes.append(
                    f"  {tx_type.title()}:"
                    f"\n    Quantity: {data['quantity']} items"
                    f"\n    Cost: ₱{data['cost']:.2f}"
                    f"\n    Revenue: ₱{data['revenue']:.2f}"
                )

    # Calculate total profit/loss
    total_profit_or_loss = total_earnings - total_losses

    # Add summary totals at the end
    summary_notes.append(f"\n=== Overall Summary ===")
    summary_notes.append(f"Total Earnings: ₱{total_earnings:.2f}")
    summary_notes.append(f"Total Losses: ₱{total_losses:.2f}")
    summary_notes.append(f"Net Profit/Loss: ₱{total_profit_or_loss:.2f}")

    # Create and return the report
    report = WeeklyReport(
        start_date=start_date,
        end_date=end_date,
        total_earnings=total_earnings,
        total_losses=total_losses,
        total_profit_or_loss=total_profit_or_loss,
        notes="\n".join(summary_notes)
    )

    return report

def generate_weekly_report_old():
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