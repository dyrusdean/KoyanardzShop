#!/usr/bin/env python
import os
import django
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

print("\n" + "="*70)
print("B2 Storage Backend Diagnostic Test")
print("="*70 + "\n")

# Test 1: Check B2 credentials
print("1. Checking B2 credentials in settings...")
from django.conf import settings
creds_ok = all([
    getattr(settings, 'B2_APPLICATION_KEY_ID', ''),
    getattr(settings, 'B2_APPLICATION_KEY', ''),
    getattr(settings, 'B2_BUCKET_NAME', ''),
    getattr(settings, 'B2_BUCKET_ID', ''),
])
print(f"   {'✓' if creds_ok else '✗'} All B2 credentials available")

# Test 2: Try to initialize B2Storage
print("\n2. Testing B2Storage backend initialization...")
try:
    from app.storage_b2 import B2Storage
    storage = B2Storage()
    print(f"   ✓ B2 Storage connected successfully!")
    print(f"   ✓ Bucket Name: {storage.bucket_name}")
    print(f"   ✓ Bucket ID: {storage.bucket_id}")
    print(f"   ✓ Endpoint: {storage.endpoint}")
except Exception as e:
    print(f"   ✗ Error connecting to B2: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Check Product model storage
print("\n3. Checking Product model 3D model field storage...")
try:
    from app.models import Product
    model_3d_field = Product._meta.get_field('model_3d')
    storage_backend = model_3d_field.storage
    
    if storage_backend is None:
        print(f"   ✗ model_3d storage is None (will use default Cloudinary)")
    elif callable(storage_backend):
        print(f"   ℹ model_3d storage is callable: {storage_backend}")
        storage_instance = storage_backend()
        storage_type = type(storage_instance).__name__
        print(f"   → Storage instance type: {storage_type}")
        if 'B2' in storage_type:
            print(f"   ✓ Will use B2Storage for 3D models")
        else:
            print(f"   ✗ Not using B2Storage: {storage_type}")
    else:
        storage_type = type(storage_backend).__name__
        print(f"   → Storage instance type: {storage_type}")
        if 'B2' in storage_type:
            print(f"   ✓ Using B2Storage for 3D models")
        else:
            print(f"   ✗ Not using B2Storage: {storage_type}")
except Exception as e:
    print(f"   ✗ Error checking Product model: {e}")

# Test 4: Check default storage
print("\n4. Checking Django's default storage...")
try:
    from django.core.files.storage import default_storage
    print(f"   Default storage type: {type(default_storage).__name__}")
    print(f"   Backend: {settings.STORAGES['default']['BACKEND']}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
print("Diagnostic complete!")
print("="*70 + "\n")
