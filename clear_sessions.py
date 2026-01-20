#!/usr/bin/env python
"""
Clear session cache for botpress keys
Run this to reset session data that might contain invalid cached keys
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone

# Clear all sessions (this will log out all users)
Session.objects.all().delete()
print("✅ Cleared all sessions - this will log out all users")

# Or if you want to be more targeted:
# from django.contrib.sessions.models import Session
# import json
# for session in Session.objects.all():
#     data = session.get_decoded()
#     if 'botpress_user_key' in str(data):
#         session.delete()
#         print(f"Cleared session with botpress cache")

print("\nNext steps:")
print("1. Reload the Django server")
print("2. Log in again")
print("3. Clear browser cookies for localhost:8000")
print("4. Send a test message - should create a new user with real key")
