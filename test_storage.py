#!/usr/bin/env python
"""Test cloudinary_storage directly"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

print("\n=== TESTING CLOUDINARY STORAGE ===\n")

# Check settings
print(f"1. Storage Configuration:")
print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"   default_storage class: {default_storage.__class__}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")

# Test upload
print(f"\n2. Testing file upload with default_storage...")
test_content = b'test file content'
test_filename = 'test_cloudinary_storage.txt'

try:
    # Save file using Django's storage
    path = default_storage.save(test_filename, ContentFile(test_content))
    print(f"   File saved to: {path}")
    
    # Get URL
    url = default_storage.url(path)
    print(f"   URL: {url}")
    
    # Check if file exists
    exists = default_storage.exists(path)
    print(f"   File exists: {exists}")
    
    # Try to access it
    import requests
    try:
        response = requests.head(url, timeout=2)
        print(f"   HTTP Status: {response.status_code}")
    except Exception as e:
        print(f"   Could not access URL: {str(e)}")
    
    # Delete test file
    default_storage.delete(path)
    print(f"   Test file deleted")
    
except Exception as e:
    print(f"   Error: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n3. Conclusion:")
print(f"   If upload worked, Cloudinary storage is configured correctly")
print(f"   If it failed, there's a configuration issue")

print(f"\n=== END TEST ===\n")
