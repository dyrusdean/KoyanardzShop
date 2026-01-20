#!/usr/bin/env python
"""Test that image uploads work end-to-end with Cloudinary storage backend"""
import os
import sys
import django
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile

# Add project to path
project_path = Path(__file__).resolve().parent
sys.path.insert(0, str(project_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage, ProductVariation
from django.contrib.auth import get_user_model
from PIL import Image
import io
import cloudinary.api

User = get_user_model()

print("=" * 80)
print("END-TO-END IMAGE UPLOAD TEST")
print("=" * 80)

# Create a simple test image
print("\n1. Creating test image...")
image = Image.new('RGB', (100, 100), color='red')
image_file = io.BytesIO()
image.save(image_file, format='PNG')
image_file.seek(0)
uploaded_image = SimpleUploadedFile(
    name='test_upload_e2e.png',
    content=image_file.getvalue(),
    content_type='image/png'
)

# Get or create test user
print("2. Getting/creating test user...")
test_user, created = User.objects.get_or_create(
    username='test_uploader',
    defaults={'email': 'test@example.com', 'is_active': True}
)
print(f"   User: {test_user.username} (created={created})")

# Create test product
print("3. Creating test product...")
try:
    product = Product.objects.create(
        product_name='E2E Test Product',
        description='Test product for e2e upload verification',
        price=9.99,
        stock=1,
    )
    print(f"   Product: {product.product_name} (created=True)")
except Exception as e:
    print(f"   ERROR creating product: {e}")
    sys.exit(1)

# Create ProductImage with upload
print("4. Uploading image to ProductImage...")
product_image = ProductImage(
    product=product,
    product_image=uploaded_image
)
product_image.save()
print(f"   ProductImage ID: {product_image.id}")
print(f"   File name: {product_image.product_image.name}")
print(f"   File URL: {product_image.product_image.url}")

# Check if file exists in Cloudinary
print("\n5. Checking if file exists in Cloudinary...")
try:
    # Get file info from Cloudinary
    resources = cloudinary.api.resources(
        type='upload',
        prefix=product_image.product_image.name
    )
    
    if resources.get('resources'):
        print(f"   ✓ File found in Cloudinary!")
        for r in resources['resources']:
            print(f"     - Public ID: {r['public_id']}")
            print(f"     - URL: {r['url']}")
            print(f"     - Type: {r['resource_type']}")
    else:
        print(f"   ✗ File NOT found in Cloudinary")
        print(f"     Search prefix: {product_image.product_image.name}")
except Exception as e:
    print(f"   ✗ Error checking Cloudinary: {e}")

# Test HTTP request to the URL
print("\n6. Testing HTTP request to file URL...")
import requests
try:
    response = requests.head(product_image.product_image.url, timeout=5)
    status = response.status_code
    print(f"   HTTP Status: {status}")
    if status == 200:
        print(f"   ✓ File is accessible!")
    else:
        print(f"   ✗ File returned HTTP {status}")
except Exception as e:
    print(f"   ✗ Error fetching URL: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
