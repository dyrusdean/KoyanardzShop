#!/usr/bin/env python
"""Test if images uploaded from now on work correctly"""
import os
import sys
import django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import Product, ProductImage
import logging

logging.basicConfig(level=logging.DEBUG)

print("\n=== TEST: UPLOAD NEW IMAGE ===\n")

# Get first product
product = Product.objects.first()
if not product:
    print("No products found!")
    exit(1)

print(f"Using product: {product.product_name} (ID: {product.id})")

# Create a test image file (pure bytes)
image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\rY\xb5\x00\x00\x00\x00IEND\xaeB`\x82'

# Create ProductImage
test_image = SimpleUploadedFile(
    name='test_new_upload.png',
    content=image_data,
    content_type='image/png'
)

img = ProductImage.objects.create(
    product=product,
    product_image=test_image,
    order=99
)

print(f"\n1. Created ProductImage with ID: {img.id}")
print(f"   Stored name (from model): {img.product_image.name}")
print(f"   Generated URL: {img.product_image.url}")

# Check if it's a valid Cloudinary URL
if 'res.cloudinary.com' in img.product_image.url:
    print(f"   ✅ URL is Cloudinary format")
    if '/product_images/' in img.product_image.url:
        print(f"   ✅ Contains product_images folder")
    if 'product_images/product_images' in img.product_image.url:
        print(f"   ❌ DOUBLE FOLDER ERROR DETECTED!")
    else:
        print(f"   ✅ No double folder issue")
else:
    print(f"   ❌ URL is NOT Cloudinary format")

print(f"\n2. Checking Cloudinary URL accessibility...")
try:
    import requests
    response = requests.head(img.product_image.url, timeout=5)
    print(f"   HTTP Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ URL is accessible!")
    elif response.status_code == 404:
        print(f"   ❌ URL returns 404 - file not found in Cloudinary!")
    else:
        print(f"   ⚠️  Unexpected status code")
except Exception as e:
    print(f"   ⚠️  Could not test URL: {str(e)}")

# Clean up
print(f"\n3. Cleaning up...")
img.delete()
print(f"   ✅ Test image deleted")

print(f"\n=== TEST COMPLETE ===\n")
