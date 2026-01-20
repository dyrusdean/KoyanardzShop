import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.test import RequestFactory
from app.views import get_product_details
import json

factory = RequestFactory()

# Test with product ID 20
product_id = 20
request = factory.get(f'/api/product/{product_id}/')
response = get_product_details(request, product_id)

print(f"Response status: {response.status_code}")
data = json.loads(response.content)
print(f"Response: {json.dumps(data, indent=2)}")
