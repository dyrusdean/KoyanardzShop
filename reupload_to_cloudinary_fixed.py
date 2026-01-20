#!/usr/bin/env python
"""Re-upload existing locally-stored product images to Cloudinary"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product
from django.conf import settings
from pathlib import Path

print("=" * 80)
print("RE-UPLOADING PRODUCT IMAGES TO CLOUDINARY")
print("=" * 80)

success_count = 0
error_count = 0

products = Product.objects.filter(image__isnull=False).exclude(image='')
print(f"Processing {products.count()} products...\n")

for product in products:
    try:
        current_path = str(product.image)
        print(f"Product {product.id}: ", end='')
        
        # Strip 'media/' prefix if present since MEDIA_ROOT already points to media/
        if current_path.startswith('media/'):
            relative_path = current_path[6:]
        else:
            relative_path = current_path
        
        file_path = Path(settings.MEDIA_ROOT) / relative_path
        
        # Check if file exists
        if not file_path.exists():
            print(f"✗ File not found")
            error_count += 1
            continue
        
        # Read the file and re-save it to trigger Cloudinary upload
        with open(file_path, 'rb') as f:
            product.image.save(
                file_path.name,
                f,
                save=True
            )
        
        print(f"✓ Uploaded")
        success_count += 1
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")
        error_count += 1

print("\n" + "=" * 80)
print(f"SUMMARY: {success_count} succeeded, {error_count} failed")
print("=" * 80)
