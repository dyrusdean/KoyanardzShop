import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product
from django.test import RequestFactory
from app.views import get_product_details
import json

# Test product 20 which now has images
product = Product.objects.get(id=20)
print(f"Product: {product.product_name} (ID: {product.id})")
print(f"Images in database: {product.images.count()}")

# Simulate the API call
factory = RequestFactory()
request = factory.get('/api/product/20/')
response = get_product_details(request, 20)

data = json.loads(response.content)
print(f"\nAPI Response:")
print(f"  Status: {data.get('status')}")
print(f"  Images returned: {len(data.get('images', []))}")

if data.get('images'):
    print(f"\nImages that should be displayed:")
    for idx, img in enumerate(data['images'], 1):
        print(f"  {idx}. {img['url']}")
else:
    print("\nNo images will be displayed (API returned empty array)")
