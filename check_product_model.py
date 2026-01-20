#!/usr/bin/env python
"""
Check if product 197 has a 3D model and verify it's stored in Backblaze B2
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from app.models import Product

print("\n" + "="*70)
print("Product 197 - 3D Model Storage Check")
print("="*70 + "\n")

try:
    product = Product.objects.get(id=197)
    print(f"✓ Product found: {product.product_name}")
    print(f"  ID: {product.id}")
    print(f"  Price: ${product.price}")
    print(f"  Stock: {product.stock}")
    
    print("\n3D Model Information:")
    print("-" * 70)
    
    if product.model_3d:
        print(f"✓ 3D model file exists")
        print(f"  Filename: {product.model_3d.name}")
        print(f"  File size: {product.model_3d.size} bytes" if hasattr(product.model_3d, 'size') else "  File size: Unknown")
        
        try:
            model_url = product.model_3d.url
            print(f"  URL: {model_url}")
            
            # Check storage location
            if 'backblazeb2.com' in model_url:
                print(f"\n  ✓✓✓ MODEL IS STORED IN BACKBLAZE B2 ✓✓✓")
            elif 'res.cloudinary.com' in model_url:
                print(f"\n  ✗✗✗ MODEL IS STORED IN CLOUDINARY (should be B2) ✗✗✗")
            else:
                print(f"\n  ℹ Storage location: {model_url.split('/')[2] if '/' in model_url else 'Unknown'}")
        except Exception as e:
            print(f"  Error getting URL: {e}")
    else:
        print("✗ No 3D model attached to this product")
    
    # Also show product images for reference
    print("\n\nProduct Images:")
    print("-" * 70)
    if product.images.exists():
        print(f"✓ {product.images.count()} image(s) found")
        for idx, img in enumerate(product.images.all(), 1):
            try:
                img_url = img.product_image.url
                storage_location = "Cloudinary" if 'res.cloudinary.com' in img_url else "Other"
                print(f"  {idx}. {img.product_image.name} ({storage_location})")
            except Exception as e:
                print(f"  {idx}. Error: {e}")
    else:
        print("✗ No images found")
    
except Product.DoesNotExist:
    print(f"✗ Product 197 not found in database")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
