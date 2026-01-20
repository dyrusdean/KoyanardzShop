#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BuynSell.settings'
    django.setup()
    
    # Test adding a product with image through the view
    from django.test import Client
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    from io import BytesIO
    import json
    
    # Create a test image
    img = Image.new('RGB', (100, 100), color='blue')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    # Use the test client instead
    client = Client()
    
    # Create form data
    img_io.seek(0)
    data = {
        'form_type': 'product',
        'product_name': 'Test Product 2',
        'category_name': '1',
        'brand': '1',
        'description': 'Test description',
        'price': '99.99',
        'stock': '10',
        'images': SimpleUploadedFile('test.png', img_io.read(), content_type='image/png')
    }
    
    # Make POST request
    response = client.post('/add_product/', data=data)
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content.decode()}")
    
    # Check if product was created with images
    from app.models import Product, ProductImage
    products = Product.objects.filter(product_name='Test Product 2')
    print(f"\nProducts created: {products.count()}")
    for p in products:
        images = p.images.all()
        print(f"Product: {p.product_name} - Images: {images.count()}")
        for img in images:
            print(f"  - {img.product_image.name}")
