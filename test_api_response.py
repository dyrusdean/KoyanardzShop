import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage
from django.http import JsonResponse
import json

# Test the API response
product_id = 20
try:
    product = Product.objects.get(id=product_id)
    
    # Get all images for the product
    images = []
    for img in product.images.all():
        images.append({
            'url': img.product_image.url,
            'id': img.id
        })
    
    # Get 3D model filename if exists
    model_3d = None
    if product.model_3d and product.model_3d.name:
        model_3d = product.model_3d.name.split('/')[-1]
    
    response = {
        'status': 'success',
        'images': images,
        'model_3d': model_3d
    }
    
    print(json.dumps(response, indent=2))
except Exception as e:
    print(f"Error: {str(e)}")
