import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage
from app.views import get_product_details
from django.test import RequestFactory

# Get a product with images
product_with_images = Product.objects.filter(images__isnull=False).first()

if product_with_images:
    print(f"Product: {product_with_images.product_name} (ID: {product_with_images.id})")
    print(f"Images in DB: {product_with_images.images.count()}")
    for img in product_with_images.images.all()[:3]:
        print(f"  - {img.product_image.name} -> {img.product_image.url}")
    
    # Now test the API endpoint
    factory = RequestFactory()
    request = factory.get(f'/api/product/{product_with_images.id}/')
    response = get_product_details(request, product_with_images.id)
    
    print(f"\nAPI Response status: {response.status_code}")
    import json
    data = json.loads(response.content)
    print(f"API Response data: {json.dumps(data, indent=2)}")
else:
    print("No products with images found")
