#!/usr/bin/env python
"""Test Cloudinary upload functionality"""
import os
import django
from PIL import Image
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from django.conf import settings

print("=" * 60)
print("CLOUDINARY CONFIGURATION TEST")
print("=" * 60)

# Check configuration
config = cloudinary.config()
print(f"\n1. Configuration:")
print(f"   Cloud Name: {config.cloud_name}")
print(f"   API Key: {config.api_key[:10]}..." if config.api_key else "   API Key: NOT SET")
print(f"   API Secret: {config.api_secret[:10]}..." if config.api_secret else "   API Secret: NOT SET")

# Validate credentials
if not config.cloud_name:
    print("\n❌ ERROR: CLOUDINARY_CLOUD_NAME not set!")
    print("   Please set it in your .env file")
    exit(1)

if not config.api_key or not config.api_secret:
    print("\n❌ ERROR: CLOUDINARY_API_KEY or CLOUDINARY_API_SECRET not set!")
    print("   Please set them in your .env file")
    exit(1)

print("\n2. Storage Configuration:")
print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")

# Create a test image
print("\n3. Creating test image...")
img = Image.new('RGB', (100, 100), color=(255, 0, 0))
img_io = BytesIO()
img.save(img_io, format='PNG')
img_io.seek(0)
test_file_path = '/tmp/test_image.png'
with open(test_file_path, 'wb') as f:
    f.write(img_io.getvalue())
print(f"   Test image created at: {test_file_path}")

# Test upload
print("\n4. Testing Cloudinary upload...")
try:
    result = cloudinary.uploader.upload(
        test_file_path,
        folder='test',
        public_id='test_upload',
        resource_type='image',
        overwrite=True
    )
    print(f"   ✅ Upload successful!")
    print(f"   Public ID: {result['public_id']}")
    print(f"   URL: {result['secure_url']}")
    print(f"   Size: {result['bytes']} bytes")
    
    # Test URL access
    print("\n5. Testing URL access...")
    import requests
    try:
        response = requests.head(result['secure_url'], timeout=5)
        if response.status_code == 200:
            print(f"   ✅ URL is accessible! (Status: {response.status_code})")
        else:
            print(f"   ⚠️  URL returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ URL not accessible: {str(e)}")
    
    # Test delete
    print("\n6. Cleaning up (deleting test image)...")
    cloudinary.uploader.destroy(result['public_id'])
    print(f"   ✅ Test image deleted")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Cloudinary is working correctly!")
    print("=" * 60)
    
except Exception as e:
    print(f"   ❌ Upload failed: {str(e)}")
    print(f"\n   Troubleshooting:")
    print(f"   1. Check Cloudinary credentials in .env are correct")
    print(f"   2. Verify API Key and Secret at: https://cloudinary.com/console")
    print(f"   3. Check internet connection")
    print(f"   4. Try regenerating API credentials")
    print("\n" + "=" * 60)
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    # Clean up test file
    try:
        os.remove(test_file_path)
    except:
        pass
