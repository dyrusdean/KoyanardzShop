#!/usr/bin/env python
"""Final verification that Cloudinary image upload pipeline is working end-to-end"""
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

from django.core.files.storage import default_storage
from django.conf import settings
from app.models import Product, ProductImage
from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile
import requests

print("=" * 80)
print("CLOUDINARY IMAGE UPLOAD - FINAL VERIFICATION")
print("=" * 80)

# 1. Verify storage configuration
print("\n✓ STORAGE CONFIGURATION")
print(f"  DEFAULT_FILE_STORAGE (STORAGES['default']): {settings.STORAGES['default']['BACKEND']}")
print(f"  Actual storage backend: {default_storage.__class__.__name__}")
print(f"  MEDIA_URL: {settings.MEDIA_URL}")
assert default_storage.__class__.__name__ == 'MediaCloudinaryStorage', "Storage backend not configured!"
print("  ✓ All storage settings correct")

# 2. Test direct storage save/load
print("\n✓ TESTING DIRECT STORAGE OPERATIONS")
test_image = Image.new('RGB', (50, 50), color='green')
image_file = io.BytesIO()
test_image.save(image_file, format='PNG')
image_file.seek(0)
uploaded_file = SimpleUploadedFile(name='verify_test.png', content=image_file.getvalue(), content_type='image/png')

saved_name = default_storage.save('test_verify/file.png', uploaded_file)
saved_url = default_storage.url(saved_name)
print(f"  Saved file name: {saved_name}")
print(f"  Generated URL: {saved_url}")

# Check if file exists
try:
    response = requests.head(saved_url, timeout=5, allow_redirects=True)
    print(f"  HTTP Status: {response.status_code}")
    assert response.status_code == 200, f"File not accessible (HTTP {response.status_code})"
    print("  ✓ File successfully uploaded to Cloudinary and accessible")
except Exception as e:
    print(f"  ✗ ERROR accessing file: {e}")
    sys.exit(1)

# 3. Test via Django model (ProductImage)
print("\n✓ TESTING PRODUCTIMAGE MODEL")
test_image2 = Image.new('RGB', (60, 60), color='blue')
image_file2 = io.BytesIO()
test_image2.save(image_file2, format='PNG')
image_file2.seek(0)
uploaded_file2 = SimpleUploadedFile(name='verify_model_test.png', content=image_file2.getvalue(), content_type='image/png')

product = Product.objects.create(
    product_name='Verification Test Product',
    description='Testing image uploads',
    price=19.99,
    stock=1,
)

product_image = ProductImage(
    product=product,
    product_image=uploaded_file2
)
product_image.save()

model_url = product_image.product_image.url
print(f"  ProductImage file name: {product_image.product_image.name}")
print(f"  ProductImage URL: {model_url}")

try:
    response = requests.head(model_url, timeout=5, allow_redirects=True)
    print(f"  HTTP Status: {response.status_code}")
    assert response.status_code == 200, f"File not accessible (HTTP {response.status_code})"
    print("  ✓ ProductImage successfully uploaded to Cloudinary and accessible")
except Exception as e:
    print(f"  ✗ ERROR accessing file: {e}")
    sys.exit(1)

# 4. Database verification
print("\n✓ DATABASE VERIFICATION")
image_count = ProductImage.objects.count()
print(f"  Total ProductImages in database: {image_count}")
assert image_count >= 1, "No images in database!"

# Check that all images have proper filenames (not broken URLs)
broken_count = 0
for img in ProductImage.objects.all():
    if not img.product_image.name.startswith('media/'):
        broken_count += 1
        print(f"    ✗ Broken filename: {img.product_image.name[:50]}")

assert broken_count == 0, f"Found {broken_count} images with broken filenames!"
print(f"  ✓ All {image_count} images have correct filename format (media/...)")

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - IMAGE UPLOAD PIPELINE IS FULLY FUNCTIONAL")
print("=" * 80)
print("\nSUMMARY:")
print("  1. ✓ Cloudinary storage backend is active")
print("  2. ✓ Direct storage operations work and files are accessible")
print("  3. ✓ ProductImage model integration works")
print("  4. ✓ Database contains only valid image records")
print("\nYou can now safely upload images from the admin panel.")
print("=" * 80)
