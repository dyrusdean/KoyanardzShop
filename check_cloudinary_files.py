#!/usr/bin/env python
"""Check what files exist in Cloudinary"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

import cloudinary
import cloudinary.api

print("\n=== CHECKING CLOUDINARY FOR EXISTING FILES ===\n")

print("1. Resources in product_images folder:")
try:
    resources = cloudinary.api.resources(type='upload', prefix='product_images', max_results=10)
    count = len(resources.get('resources', []))
    print(f"   Found {count} resources:")
    for r in resources.get('resources', []):
        print(f"     - {r['public_id']}")
except Exception as e:
    print(f"   Error: {str(e)}")

print("\n2. Resources in products folder:")
try:
    resources = cloudinary.api.resources(type='upload', prefix='products', max_results=10)
    count = len(resources.get('resources', []))
    print(f"   Found {count} resources:")
    for r in resources.get('resources', []):
        print(f"     - {r['public_id']}")
except Exception as e:
    print(f"   Error: {str(e)}")

print("\n=== CONCLUSION ===")
print("If files are NOT in Cloudinary, that's why you get 404 errors!")
print("The upload signal is not successfully uploading files to Cloudinary")
print("despite the database showing Cloudinary URLs.\n")
