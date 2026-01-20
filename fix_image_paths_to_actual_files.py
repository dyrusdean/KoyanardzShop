#!/usr/bin/env python
"""Fix product image paths in database to match actual file locations"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product
from django.conf import settings

print("=" * 80)
print("FIXING PRODUCT IMAGE PATHS IN DATABASE")
print("=" * 80)

fixed_count = 0

for product in Product.objects.filter(image__isnull=False).exclude(image=''):
    current_path = str(product.image)
    
    # Remove 'media/' prefix for checking
    check_path = current_path[6:] if current_path.startswith('media/') else current_path
    
    # Check if file exists at current location
    file_path = Path(settings.MEDIA_ROOT) / check_path
    
    if not file_path.exists():
        # Try to find the file with alternative paths
        filename = Path(check_path).name
        
        # Check if it's in products instead of product_images
        if 'product_images/' in check_path:
            alt_path = check_path.replace('product_images/', 'products/')
            alt_file = Path(settings.MEDIA_ROOT) / alt_path
            
            if alt_file.exists():
                # Update database to point to correct location
                product.image = f'media/{alt_path}'
                product.save()
                print(f"✓ Product {product.id}: Updated path to media/{alt_path}")
                fixed_count += 1
                continue
        
        # Check products/variants
        alt_path = f'products/variants/{filename}'
        alt_file = Path(settings.MEDIA_ROOT) / alt_path
        if alt_file.exists():
            product.image = f'media/{alt_path}'
            product.save()
            print(f"✓ Product {product.id}: Updated path to media/{alt_path}")
            fixed_count += 1
            continue

print("\n" + "=" * 80)
print(f"FIXED: {fixed_count} product image paths")
print("=" * 80)
