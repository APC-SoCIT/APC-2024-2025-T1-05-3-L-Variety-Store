from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json

@csrf_exempt
def scan_barcode(request):
    if request.method == "POST":
        data = json.loads(request.body)
        barcodes = data.get('barcodes', [])  # Accepting multiple barcodes

        if not barcodes:
            return JsonResponse({"success": False, "message": "No barcodes provided."})

        scanned_products = []
        errors = []
        
        for barcode in barcodes:
            product = Product.objects.filter(barcode=barcode).first()

            if not product:
                errors.append(f"Product with barcode {barcode} not found.")
                continue

            if product.quantity <= 0:
                errors.append(f"Product '{product.name}' (barcode: {barcode}) is out of stock.")
                continue

            # Deduct 1 item per scan
            product.quantity -= 1
            product.save()

            scanned_products.append({
                "name": product.name,
                "barcode": product.barcode,
                "remaining_quantity": product.quantity,
                "price": float(product.price),
            })

        response_data = {
            "success": True if scanned_products else False,
            "scanned_products": scanned_products,
            "errors": errors
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method."})
    
    
from django.shortcuts import render

# View function for the storefront page
def storefront_view(request):
    # Any context data you want to pass to the template (e.g., product data)
    context = {
        'products': [
            {'name': 'Product 1', 'price': 19.99},
            {'name': 'Product 2', 'price': 29.99},
            {'name': 'Product 3', 'price': 39.99},
        ],
    }
    
    return render(request, 'storefront.html', context)
