#!/usr/bin/env python
"""
Debug DownloadedFile object
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

product = Product.objects.get(id=197)
if product.model_3d:
    storage = product.model_3d.storage
    file_name = product.model_3d.name
    
    print(f"File name: {file_name}")
    print(f"Storage type: {type(storage)}")
    
    # Get the file
    file_version = storage.bucket.get_file_info_by_name(file_name)
    downloaded_file = storage.bucket.download_file_by_id(file_version.id_)
    
    print(f"\nDownloadedFile type: {type(downloaded_file)}")
    
    # Check response
    if hasattr(downloaded_file, 'response'):
        resp = downloaded_file.response
        print(f"\nResponse: {type(resp)}")
        print(f"Response attrs: {[x for x in dir(resp) if not x.startswith('_')]}")
        
        # Try to read from response
        if hasattr(resp, 'read'):
            content = resp.read()
            print(f"\nRead {len(content)} bytes")
        elif hasattr(resp, 'content'):
            print(f"\nResponse has content: {type(resp.content)}")
    
    # Alternative: use save_to
    print(f"\nDownloadedFile methods: ['check_hash', 'save', 'save_to']")
    print("Has save_to method")
