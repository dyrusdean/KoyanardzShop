#!/usr/bin/env python
"""
Migration helper script - Run this to apply database migrations
Usage: python migrate_now.py
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from django.core.management import call_command
    
    print("\n" + "="*60)
    print("Applying Django migrations...")
    print("="*60 + "\n")
    
    call_command('migrate', verbosity=2)
    
    print("\n" + "="*60)
    print("✅ Migrations applied successfully!")
    print("="*60)
    print("\nNow you can:")
    print("1. Clear browser cookies for localhost:8000")
    print("2. Restart Django server: python manage.py runserver")
    print("3. Test the chat again")
    print("\n")
    
except Exception as e:
    print("\n" + "="*60)
    print(f"❌ Error applying migrations: {e}")
    print("="*60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
