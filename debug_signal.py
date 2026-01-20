#!/usr/bin/env python
"""Debug: Check if the signal is being triggered"""
import os
import sys
import django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')

# Set up logging BEFORE django.setup()
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import Product, ProductImage
import cloudinary
import cloudinary.uploader

print("\n=== CHECKING SIGNAL BEHAVIOR ===\n")

# Check Cloudinary config
config = cloudinary.config()
print(f"1. Cloudinary configured:")
print(f"   Cloud Name: {config.cloud_name}")
print(f"   API Key: {config.api_key[:10]}..." if config.api_key else "   API Key: NOT SET")

# Get product
product = Product.objects.first()
print(f"\n2. Using product: {product.product_name}")

# Check current images
print(f"\n3. Current images for this product: {product.images.count()}")
for img in product.images.all()[:3]:
    print(f"   - {img.product_image.name}: {img.product_image.url}")

# Create a test image
print(f"\n4. Creating test image...")
image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\rY\xb5\x00\x00\x00\x00IEND\xaeB`\x82'

test_image = SimpleUploadedFile(
    name='debug_test.png',
    content=image_data,
    content_type='image/png'
)

print(f"   - File size: {len(image_data)} bytes")
print(f"   - File name: {test_image.name}")

# This should trigger the signal
print(f"\n5. Creating ProductImage (this should trigger signal)...")
img = ProductImage.objects.create(
    product=product,
    product_image=test_image,
    order=999
)

print(f"   ✅ ProductImage created with ID: {img.id}")

# Refresh from DB to see what was saved
img.refresh_from_db()
print(f"\n6. After signal execution:")
print(f"   Stored name: {img.product_image.name}")
print(f"   URL: {img.product_image.url}")

# Check if name changed (signal should have changed it)
if img.product_image.name.startswith('product_images/product_images/'):
    print(f"   ❌ DOUBLE FOLDER - signal saved incorrectly")
elif img.product_image.name.startswith('product_images/'):
    print(f"   ✅ Correct format - signal worked")
else:
    print(f"   ⚠️  Unexpected format")

# Clean up
print(f"\n7. Cleaning up...")
img.delete()
print(f"   ✅ Done")

print(f"\n=== END DEBUG ===\n")
