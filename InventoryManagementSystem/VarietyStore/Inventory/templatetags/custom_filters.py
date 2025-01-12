from django import template

register = template.Library()

@register.filter
def format_price(value, currency="USD"):
    """
    Formats the price with the given currency symbol.
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    
    symbols = {
        "USD": "$",
        "PHP": "₱",
        "EUR": "€",
        "JPY": "¥",
        "GBP": "£",
    }
    currency_symbol = symbols.get(currency, currency)
    return f"{currency_symbol}{value:,.2f}"
