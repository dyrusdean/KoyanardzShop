#!/usr/bin/env python
"""Test if product images are accessible from the web"""
import requests
import os
import sys
import django
from pathlib import Path

project_path = Path(__file__).resolve().parent
sys.path.insert(0, str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage

print("=" * 80)
print("PRODUCT IMAGE ACCESSIBILITY TEST")
print("=" * 80)

# Test Product main images
print("\n1. TESTING PRODUCT MAIN IMAGES:")
products_with_images = Product.objects.filter(image__isnull=False)[:5]
for p in products_with_images:
    url = p.image.url
    try:
        response = requests.head(url, timeout=3)
        status = response.status_code
        print(f"  Product {p.id} ({p.product_name[:30]}):")
        print(f"    URL: {url[:80]}")
        print(f"    Status: {status} {'✓' if status == 200 else '✗'}")
    except Exception as e:
        print(f"  Product {p.id}: ERROR - {str(e)[:60]}")

# Test ProductImages
print("\n2. TESTING PRODUCTIMAGES:")
product_images = ProductImage.objects.all()[:5]
for img in product_images:
    url = img.product_image.url
    try:
        response = requests.head(url, timeout=3)
        status = response.status_code
        print(f"  ProductImage {img.id} (Product {img.product.id}):")
        print(f"    URL: {url[:80]}")
        print(f"    Status: {status} {'✓' if status == 200 else '✗'}")
    except Exception as e:
        print(f"  ProductImage {img.id}: ERROR - {str(e)[:60]}")

print("\n" + "=" * 80)
