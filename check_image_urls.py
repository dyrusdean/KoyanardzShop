#!/usr/bin/env python
"""Check image URLs in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage

print("\n=== CHECKING PRODUCT IMAGES IN DATABASE ===\n")

# Check a few products
products = Product.objects.all()[:3]
for product in products:
    print(f"Product: {product.product_name} (ID: {product.id})")
    print(f"  Main image stored name: {product.image.name}")
    print(f"  Main image URL: {product.image.url}")
    
    # Check associated images
    images = product.images.all()[:2]
    print(f"  Associated images ({product.images.count()} total):")
    for img in images:
        print(f"    - Stored name: {img.product_image.name}")
        print(f"      Generated URL: {img.product_image.url}")
    print()

# Now check what the actual issue is
print("\n=== ANALYZING THE 404 ERROR ===\n")
print("The 404 errors suggest that:")
print("1. Files are being stored with a path that Cloudinary doesn't have")
print("2. The public_id in the database doesn't match what was uploaded")
print("\nLet's check one specific image that's failing:")

# Get a product with images
product_with_images = Product.objects.filter(images__isnull=False).first()
if product_with_images:
    img = product_with_images.images.first()
    if img:
        print(f"\nExample:")
        print(f"  Stored name: {img.product_image.name}")
        print(f"  Generated URL: {img.product_image.url}")
        
        # What should it be?
        print(f"\n  The URL should contain the public_id from Cloudinary upload")
        print(f"  If stored name is 'product_images/filename', URL becomes:")
        print(f"  https://res.cloudinary.com/dewtkzljk/image/upload/product_images/filename")
