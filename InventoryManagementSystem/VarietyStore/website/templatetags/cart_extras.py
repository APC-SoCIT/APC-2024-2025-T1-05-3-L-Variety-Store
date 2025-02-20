from django import template

register = template.Library()

@register.filter
def cart_total(cart_items):
    return sum(item.product.product_price * item.quantity for item in cart_items)