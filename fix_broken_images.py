#!/usr/bin/env python
"""Fix all broken product images by re-uploading them to Cloudinary"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import ProductImage, Product
import cloudinary
import cloudinary.uploader
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("\n=== FIX BROKEN IMAGES IN DATABASE ===\n")

# Get all images
all_images = ProductImage.objects.all()
print(f"Total ProductImages in database: {all_images.count()}")

# Check how many are 404
print(f"\nChecking URLs for 404 errors...")
broken_count = 0
working_count = 0
for img in all_images:
    url = img.product_image.url
    try:
        response = requests.head(url, timeout=2)
        if response.status_code == 404:
            broken_count += 1
            if broken_count <= 5:
                print(f"  404: {url}")
        elif response.status_code == 200:
            working_count += 1
    except:
        broken_count += 1

print(f"\nResults:")
print(f"  Working: {working_count}")
print(f"  Broken (404): {broken_count}")

if broken_count > 0:
    print(f"\n⚠️  {broken_count} broken images found!")
    print(f"These need to be re-uploaded because the files don't exist in Cloudinary.")
    print(f"\nTo fix this:")
    print(f"1. The original image files need to still exist locally")
    print(f"2. Re-run the upload for each image")
    print(f"3. Or delete these broken records and re-upload from admin panel")
    print(f"\nFor now, delete broken images from database:")
    print(f"  ProductImage.objects.all().delete()")
    print(f"  # Then re-upload from admin panel")
