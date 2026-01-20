#!/usr/bin/env python
"""Fix Product.image and Product.model_3d path prefixes in database"""
import os, django
from pathlib import Path

project_path = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(project_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

print("=" * 80)
print("FIXING PRODUCT IMAGE & MODEL_3D PATHS")
print("=" * 80)

# Fix Product.image
print("\n1. FIXING Product.image paths...")
fixed_count = 0
for p in Product.objects.filter(image__isnull=False):
    old_path = str(p.image)
    # If path doesn't start with "media/", add it
    if not old_path.startswith("media/"):
        new_path = f"media/{old_path}"
        p.image = new_path
        p.save()
        fixed_count += 1
        print(f"   Product {p.id}: '{old_path}' → '{new_path}'")
        
print(f"   ✓ Fixed {fixed_count} Product.image paths")

# Fix Product.model_3d
print("\n2. FIXING Product.model_3d paths...")
fixed_count = 0
for p in Product.objects.filter(model_3d__isnull=False):
    old_path = str(p.model_3d)
    # If path doesn't start with "media/", add it
    if not old_path.startswith("media/"):
        new_path = f"media/{old_path}"
        p.model_3d = new_path
        p.save()
        fixed_count += 1
        print(f"   Product {p.id}: '{old_path}' → '{new_path}'")
        
print(f"   ✓ Fixed {fixed_count} Product.model_3d paths")

print("\n" + "=" * 80)
print("✓ ALL PATHS FIXED")
print("=" * 80)
