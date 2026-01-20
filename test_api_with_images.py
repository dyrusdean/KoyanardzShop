import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.test import RequestFactory
from app.views import get_product_details
from app.models import Product
import json

factory = RequestFactory()

# Find a product with images
product = Product.objects.filter(images__isnull=False).first()

if product:
    print(f"Product: {product.product_name} (ID: {product.id})")
    print(f"Images in DB: {product.images.count()}")
    
    # Test the API
    request = factory.get(f'/api/product/{product.id}/')
    response = get_product_details(request, product.id)
    
    print(f"\nAPI Response status: {response.status_code}")
    data = json.loads(response.content)
    print(f"API Response: {json.dumps(data, indent=2)}")
else:
    print("No products with images found")
