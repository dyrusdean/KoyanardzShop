#!/usr/bin/env python
"""
Test the 3D model proxy endpoint
"""
import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.test import Client
from django.test.utils import override_settings
from app.models import Product

print("\n" + "="*70)
print("3D Model Proxy Endpoint Test")
print("="*70 + "\n")

product_id = 197

try:
    product = Product.objects.get(id=product_id)
    print(f"Testing proxy endpoint for product: {product.product_name}")
    print(f"Product ID: {product_id}")
    print()
    
    if not product.model_3d:
        print("✗ Product has no 3D model")
    else:
        # Test the proxy endpoint
        endpoint = f'/api/product/{product_id}/model-3d/'
        print(f"Endpoint: {endpoint}")
        print()
        
        # Use override_settings to bypass ALLOWED_HOSTS check in test
        with override_settings(ALLOWED_HOSTS=['*']):
            client = Client()
            response = client.get(endpoint)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Endpoint returned 200 OK")
                
                # Check CORS headers
                print("\nCORS Headers:")
                cors_headers = {
                    'Access-Control-Allow-Origin': response.get('Access-Control-Allow-Origin', 'NOT SET'),
                    'Access-Control-Allow-Methods': response.get('Access-Control-Allow-Methods', 'NOT SET'),
                    'Cache-Control': response.get('Cache-Control', 'NOT SET'),
                    'Content-Type': response.get('Content-Type', 'NOT SET'),
                }
                
                for header, value in cors_headers.items():
                    status = "✓" if value != 'NOT SET' else "ℹ"
                    print(f"  {status} {header}: {value}")
                
                # Check file size
                content_length = response.get('Content-Length')
                print(f"\n✓ File size: {content_length} bytes" if content_length else "ℹ Content-Length not set")
                
                print("\n✓✓✓ PROXY ENDPOINT IS WORKING ✓✓✓")
            else:
                print(f"✗ Endpoint returned {response.status_code}")
                if response.status_code == 404:
                    print("  Reason: Model not found (endpoint might not be registered)")
                print(f"  Response preview: {str(response.content[:200])}")
        
except Product.DoesNotExist:
    print(f"✗ Product {product_id} not found")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
