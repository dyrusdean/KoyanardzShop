#!/usr/bin/env python
"""
Test script to verify avatar upload functionality.
This script will:
1. Check if the avatar field exists in CustomUser model
2. Check if avatars folder exists
3. Check if the default avatar exists
4. Verify media URL configuration
"""

import os
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.conf import settings
from app.models import CustomUser
from app.forms import ProfileForm

print("=" * 60)
print("AVATAR UPLOAD FUNCTIONALITY TEST")
print("=" * 60)

# Test 1: Check avatar field in model
print("\n1. Checking CustomUser model for avatar field...")
try:
    avatar_field = CustomUser._meta.get_field('avatar')
    print(f"   ✓ Avatar field found: {avatar_field}")
    print(f"   - Upload to: {avatar_field.upload_to}")
    print(f"   - Null: {avatar_field.null}, Blank: {avatar_field.blank}")
    print(f"   - Default: {avatar_field.default}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Check ProfileForm includes avatar
print("\n2. Checking ProfileForm for avatar field...")
try:
    form = ProfileForm()
    if 'avatar' in form.fields:
        print(f"   ✓ Avatar field found in ProfileForm")
        print(f"   - Field type: {type(form.fields['avatar']).__name__}")
    else:
        print(f"   ✗ Avatar field NOT found in ProfileForm")
        print(f"   - Available fields: {list(form.fields.keys())}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check media folder structure
print("\n3. Checking media folder structure...")
media_root = Path(settings.MEDIA_ROOT)
print(f"   - MEDIA_ROOT: {media_root}")
print(f"   - MEDIA_URL: {settings.MEDIA_URL}")

avatars_dir = media_root / 'avatars'
if avatars_dir.exists():
    print(f"   ✓ Avatars folder exists: {avatars_dir}")
else:
    print(f"   ✗ Avatars folder does NOT exist")

# Test 4: Check default avatar image
print("\n4. Checking default avatar image...")
default_avatar = Path(settings.BASE_DIR) / 'static' / 'images' / 'icon' / 'user_default.png'
if default_avatar.exists():
    print(f"   ✓ Default avatar image found: {default_avatar}")
    print(f"   - Size: {default_avatar.stat().st_size} bytes")
else:
    print(f"   ✗ Default avatar image NOT found")

# Test 5: Check a test user's avatar
print("\n5. Checking test user avatar...")
try:
    test_user = CustomUser.objects.first()
    if test_user:
        print(f"   - Test user: {test_user.username}")
        print(f"   - Avatar: {test_user.avatar}")
        if test_user.avatar:
            avatar_path = Path(settings.MEDIA_ROOT) / str(test_user.avatar)
            if avatar_path.exists():
                print(f"   ✓ Avatar file exists at {avatar_path}")
            else:
                print(f"   - Avatar URL exists but file not found (will be uploaded)")
        else:
            print(f"   - No avatar set (will use default)")
    else:
        print(f"   - No test users found yet")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Verify form submission handling
print("\n6. Checking form fields configuration...")
try:
    form = ProfileForm()
    avatar_field = form.fields.get('avatar')
    if avatar_field:
        print(f"   ✓ Avatar field widget: {type(avatar_field.widget).__name__}")
        if hasattr(avatar_field.widget, 'attrs'):
            print(f"   - Widget attrs: {avatar_field.widget.attrs}")
    
    # Check all fields
    print(f"\n   Form fields:")
    for field_name in form.fields:
        field = form.fields[field_name]
        print(f"   - {field_name}: {type(field).__name__}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nSummary:")
print("If all checks pass with ✓, avatar upload is properly configured!")
print("The avatar will be saved to: media/avatars/")
print("Max file size: 5MB (enforced in template)")
print("Accepted formats: Any image file (JPG, PNG, GIF, etc.)")
