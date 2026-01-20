import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.test import RequestFactory
from app.views import get_product_details
import json

factory = RequestFactory()

# Test products from the screenshot
product_ids = [20, 21, 26]

for prod_id in product_ids:
    request = factory.get(f'/api/product/{prod_id}/')
    response = get_product_details(request, prod_id)
    data = json.loads(response.content)
    
    print(f"Product {prod_id}:")
    print(f"  Images returned: {len(data.get('images', []))}")
    for img in data.get('images', []):
        is_main = " (MAIN)" if img.get('is_main') else ""
        print(f"    - {img['url']}{is_main}")
    print()
