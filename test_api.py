import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage

# Get first product
p = Product.objects.first()
if p:
    print(f'Product ID: {p.id}')
    print(f'Product Name: {p.product_name}')
    print(f'Images count: {p.images.count()}')
    for img in p.images.all():
        print(f'  - Image: {img.product_image.url}')
    print(f'Model 3D: {p.model_3d.name if p.model_3d else "None"}')
else:
    print('No products found')
