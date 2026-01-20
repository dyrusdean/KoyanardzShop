#!/usr/bin/env python
"""Fix ALL product image paths in database to match actual file locations"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product
from django.conf import settings

print("=" * 80)
print("SCANNING AND FIXING PRODUCT IMAGE PATHS")
print("=" * 80)

# First, find ALL files in media/products
media_products = Path(settings.MEDIA_ROOT) / 'products'
if media_products.exists():
    all_files = {}
    for f in media_products.rglob('*'):
        if f.is_file():
            all_files[f.name] = str(f.relative_to(settings.MEDIA_ROOT))
    
    print(f"Found {len(all_files)} files in media/products/\n")
    
    # Now check each product in database
    fixed_count = 0
    not_found = []
    
    for product in Product.objects.filter(image__isnull=False).exclude(image=''):
        current = str(product.image)
        filename = Path(current).name
        
        # Check if we have this file
        if filename in all_files:
            actual_path = all_files[filename]
            if actual_path != current.replace('media/', ''):
                # Path mismatch, update it
                product.image = f'media/{actual_path}'
                product.save()
                print(f"[OK] Product {product.id}: {filename}")
                fixed_count += 1
        else:
            not_found.append((product.id, filename))
    
    print("\n" + "=" * 80)
    print(f"FIXED: {fixed_count} products")
    if not_found:
        print(f"NOT FOUND: {len(not_found)} products (files missing from media/products/)")
        for pid, fname in not_found[:5]:
            print(f"  Product {pid}: {fname}")
    print("=" * 80)
