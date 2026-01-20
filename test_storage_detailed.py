#!/usr/bin/env python
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

# Now test storage
from django.conf import settings
from django.core.files.storage import default_storage
import cloudinary

print("=" * 80)
print("CLOUDINARY CONFIGURATION DIAGNOSTIC")
print("=" * 80)

# Check Cloudinary config
print("\n1. CLOUDINARY CREDENTIALS:")
print(f"   CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
print(f"   CLOUDINARY_API_KEY: {os.getenv('CLOUDINARY_API_KEY', '')[:10]}...")
print(f"   CLOUDINARY_API_SECRET: {os.getenv('CLOUDINARY_API_SECRET', '')[:10]}...")

# Check cloudinary module
print("\n2. CLOUDINARY MODULE CONFIG:")
print(f"   cloudinary.config.cloud_name: {cloudinary.config().cloud_name}")
print(f"   cloudinary.config.api_key: {cloudinary.config().api_key}")

# Check Django settings
print("\n3. DJANGO STORAGE SETTINGS:")
print(f"   STORAGES config: {settings.STORAGES}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")

# Check installed apps
print("\n4. INSTALLED_APPS (cloudinary-related):")
has_cloudinary = 'cloudinary' in settings.INSTALLED_APPS
has_cloudinary_storage = 'cloudinary_storage' in settings.INSTALLED_APPS
print(f"   'cloudinary' installed: {has_cloudinary}")
print(f"   'cloudinary_storage' installed: {has_cloudinary_storage}")

# Check actual storage backend in use
print("\n5. ACTUAL STORAGE BACKEND IN USE:")
print(f"   default_storage class: {default_storage.__class__}")
print(f"   default_storage module: {default_storage.__class__.__module__}")

# Try to access the backend directly
from cloudinary_storage.storage import MediaCloudinaryStorage
print(f"\n6. CLOUDINARY STORAGE CLASS CHECK:")
print(f"   MediaCloudinaryStorage imported: OK")
print(f"   Is default_storage an instance? {isinstance(default_storage, MediaCloudinaryStorage)}")

# Check if there's an environment issue
print("\n7. ENVIRONMENT CHECK:")
import importlib
try:
    cloudinary_storage_module = importlib.import_module('cloudinary_storage.storage')
    print(f"   cloudinary_storage module imported: OK")
except ImportError as e:
    print(f"   cloudinary_storage import FAILED: {e}")

# Try instantiating directly
print("\n8. DIRECT INSTANTIATION TEST:")
try:
    from cloudinary_storage.storage import MediaCloudinaryStorage
    test_storage = MediaCloudinaryStorage()
    print(f"   MediaCloudinaryStorage() instantiated: OK")
    print(f"   Test location: {test_storage.location}")
except Exception as e:
    print(f"   MediaCloudinaryStorage() FAILED: {e}")

print("\n" + "=" * 80)
