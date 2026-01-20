#!/usr/bin/env python
"""Re-upload existing locally-stored product images to Cloudinary"""
import os, django
from pathlib import Path

project_path = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(project_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product
from django.core.files.storage import default_storage
from django.conf import settings

print("=" * 80)
print("RE-UPLOADING PRODUCT IMAGES TO CLOUDINARY")
print("=" * 80)

reupload_count = 0
error_count = 0

for product in Product.objects.filter(image__isnull=False):
    if not product.image:
        continue
        
    image_path = str(product.image)
    print(f"\nProduct {product.id} ({product.product_name[:40]}):")
    print(f"  Current path: {image_path}")
    
    # Try to read the file from local storage
    try:
        # Get the local file
        local_file_path = Path(settings.MEDIA_ROOT) / image_path if settings.MEDIA_ROOT else Path('media') / image_path
        
        if local_file_path.exists():
            # Read the file
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Force save to Cloudinary by clearing and re-assigning
            # This triggers the storage backend to save to Cloudinary
            product.image.save(
                product.image.name,
                open(local_file_path, 'rb'),
                save=False
            )
            product.save()
            print(f"  ✓ Re-uploaded to Cloudinary")
            print(f"  New URL: {product.image.url[:80]}")
            reupload_count += 1
        else:
            print(f"  ✗ Local file not found: {local_file_path}")
            error_count += 1
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")
        error_count += 1

print("\n" + "=" * 80)
print(f"✓ Re-uploaded: {reupload_count} images")
print(f"✗ Errors: {error_count}")
print("=" * 80)
