#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage

# Get all products
products = Product.objects.all()[:5]
print(f"Total products in DB: {Product.objects.count()}\n")

for product in products:
    images = product.images.all()
    print(f"Product ID: {product.id}")
    print(f"  Name: {product.product_name}")
    print(f"  3D Model: {product.model_3d.name if product.model_3d else 'None'}")
    print(f"  Images count: {images.count()}")
    for img in images:
        print(f"    - {img.product_image.url if img.product_image else 'No URL'}")
    print()
