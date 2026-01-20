#!/usr/bin/env python
"""Clean up broken image URLs from database"""
import os
import sys
import django
from pathlib import Path

# Add project to path
project_path = Path(__file__).resolve().parent
sys.path.insert(0, str(project_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import ProductImage, Product
import requests

print("=" * 80)
print("CLEANUP: REMOVING BROKEN IMAGE URLS FROM DATABASE")
print("=" * 80)

# Find all ProductImages
all_images = ProductImage.objects.all()
print(f"\nTotal ProductImages in database: {all_images.count()}")

broken_images = []
working_images = []

print("\nChecking each image (by filename pattern)...")
# Images uploaded with the OLD system have URLs like this (with full URLs stored)
# vs new system which stores just the filename like "media/product_images/..."

for img in all_images:
    filename = img.product_image.name if img.product_image else ""
    
    # New correct format: starts with "media/product_images/"
    if filename.startswith("media/product_images/"):
        working_images.append(img)
        print(f"  ✓ ID {img.id}: {filename[:70]}")
    else:
        broken_images.append(img)
        print(f"  ✗ ID {img.id}: {filename[:70]}")

print(f"\n\nSUMMARY:")
print(f"  Working images: {len(working_images)}")
print(f"  Broken images: {len(broken_images)}")

if broken_images:
    print(f"\nDELETING {len(broken_images)} broken images...")
    deleted_count, _ = ProductImage.objects.filter(id__in=[img.id for img in broken_images]).delete()
    print(f"  ✓ Deleted {deleted_count} broken image records")
    
    # Also check for Product main images that are broken
    print(f"\nChecking Product main images...")
    broken_products = []
    for product in Product.objects.all():
        if product.image:
            filename = product.image.name if product.image else ""
            # New correct format: starts with "media/products/"
            if not filename.startswith("media/products/"):
                broken_products.append(product)
                print(f"  ✗ Product {product.id} main image: {filename[:70]}")
    
    if broken_products:
        print(f"\nCleaning broken Product main images...")
        for product in broken_products:
            product.image.delete(save=False)
            product.save()
            print(f"  ✓ Cleared Product {product.id} main image")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
