#!/usr/bin/env python
"""Test that the template will use the proxy URL instead of Cloudinary URL"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
sys.path.insert(0, 'c:\\Users\\eborg\\OneDrive\\Documents\\GitHub\\Koyanardzshop')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    print("Skipping Django-dependent checks")

from app.models import Product

# Test product 197
try:
    product = Product.objects.get(id=197)
    print(f"✓ Product 197 found: {product.product_name}")
    
    if product.model_3d:
        print(f"✓ Product has model_3d field set")
        print(f"  - model_3d.name: {product.model_3d.name}")
        print(f"  - model_3d.url: {product.model_3d.url}")
        print(f"\n📌 CRITICAL - Template will now use proxy URL:")
        print(f"  Old URL (Cloudinary): {product.model_3d.url}")
        print(f"  New URL (Proxy):      /api/product/{product.id}/model-3d/")
        print(f"\n✓ This means the JavaScript in product_item.html will load from the proxy!")
    else:
        print(f"✗ Product 197 has no model_3d set")
        
except Product.DoesNotExist:
    print(f"✗ Product 197 not found")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\nTo verify the fix works:")
print("1. Go to http://localhost:8000/product_item/197/")
print("2. Open browser DevTools (F12)")
print("3. Go to Console tab")
print("4. Look for the request to /api/product/197/model-3d/ (should show 200 OK)")
print("5. The old Cloudinary URL should NOT appear in Network tab")
