#!/usr/bin/env python
"""
Test B2 file accessibility and CORS headers
"""
import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

print("\n" + "="*70)
print("B2 File Accessibility & CORS Test")
print("="*70 + "\n")

# Get product 197
try:
    product = Product.objects.get(id=197)
    if product.model_3d:
        model_url = product.model_3d.url
        print(f"Product: {product.product_name}")
        print(f"Model URL: {model_url}")
        print()
        
        # Test if the URL is accessible
        print("Testing URL accessibility...")
        try:
            response = requests.head(model_url, timeout=5, allow_redirects=True)
            print(f"✓ URL is accessible")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {response.headers.get('Content-Length', 'N/A')} bytes")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'NOT SET'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'NOT SET'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'NOT SET'),
            }
            
            print("\n  CORS Headers:")
            for header, value in cors_headers.items():
                status = "✓" if value != 'NOT SET' else "✗"
                print(f"    {status} {header}: {value}")
            
            # Try to actually download a bit of the file
            print("\n  Attempting to download file...")
            response = requests.get(model_url, timeout=5, stream=True)
            chunk = next(response.iter_content(chunk_size=1024), None)
            if chunk:
                print(f"  ✓ Successfully downloaded {len(chunk)} bytes from file")
            
        except requests.exceptions.Timeout:
            print(f"✗ URL timeout (B2 might be slow or unreachable)")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("✗ Product 197 has no 3D model")
except Product.DoesNotExist:
    print("✗ Product 197 not found")

print("\n" + "="*70)
print("Accessibility Test Complete")
print("="*70 + "\n")
