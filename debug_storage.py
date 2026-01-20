#!/usr/bin/env python
"""Debug the file storage behavior"""
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
from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile

print("=" * 80)
print("STORAGE DEBUG")
print("=" * 80)

# Create a test image
image = Image.new('RGB', (100, 100), color='blue')
image_file = io.BytesIO()
image.save(image_file, format='PNG')
image_file.seek(0)
uploaded_image = SimpleUploadedFile(
    name='debug_storage_test.png',
    content=image_file.getvalue(),
    content_type='image/png'
)

print(f"\n1. Storage backend: {default_storage.__class__.__name__}")
print(f"2. Storage location: {default_storage.location if hasattr(default_storage, 'location') else 'N/A'}")

# Test saving a file
filename = 'test_folder/debug_test_file.png'
print(f"\n3. Saving file with name: {filename}")
saved_name = default_storage.save(filename, uploaded_image)
print(f"   Returned name: {saved_name}")

# Check the URL
url = default_storage.url(saved_name)
print(f"\n4. URL generated: {url}")

# Check if file exists
exists = default_storage.exists(saved_name)
print(f"   File exists: {exists}")

# Try accessing the file
print(f"\n5. Checking HTTP access to URL...")
import requests
try:
    response = requests.head(url, timeout=5, allow_redirects=True)
    print(f"   HTTP Status: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
