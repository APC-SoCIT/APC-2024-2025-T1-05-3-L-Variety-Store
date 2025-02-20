from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Initialize products in the database'

    def handle(self, *args, **kwargs):
        products = [
            {'name': 'Liempo (Per kg)', 'price': 230, 'category': 'meat'},
            {'name': 'Lechon Roll (Per kg)', 'price': 200, 'category': 'meat'},
            {'name': 'Bacon (Per kg)', 'price': 215, 'category': 'meat'},
            {'name': 'Chicken Drumsticks (Per kg)', 'price': 180, 'category': 'meat'},
            {'name': 'Chicken Wings (Per kg)', 'price': 120, 'category': 'meat'},
            {'name': 'Eggplant (Per kg)', 'price': 40, 'category': 'vegetable'},
            {'name': 'Carrots (Per kg)', 'price': 80, 'category': 'vegetable'},
            {'name': 'Sayote (Per kg)', 'price': 50, 'category': 'vegetable'},
            {'name': 'Potatoes (Per kg)', 'price': 80, 'category': 'vegetable'},
            {'name': 'Garlic (Per kg)', 'price': 103.63, 'category': 'vegetable'},
            {'name': 'Onion (Per kg)', 'price': 89.13, 'category': 'vegetable'},
        ]

        for product_data in products:
            Product.objects.get_or_create(**product_data)

        self.stdout.write(self.style.SUCCESS('Successfully initialized products'))
