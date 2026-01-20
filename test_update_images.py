import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from app.models import Product, ProductImage

# Create a test image
def create_test_image(name='test.png'):
    img = Image.new('RGB', (100, 100), color='green')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return SimpleUploadedFile(name, img_io.read(), content_type='image/png')

# Get an existing product
product = Product.objects.first()
if not product:
    print("No products found!")
    exit(1)

print(f"Testing with product ID {product.id}: {product.product_name}")
print(f"Current images: {product.images.count()}")

# Delete existing images
product.images.all().delete()
print(f"Images after cleanup: {product.images.count()}")

# Update product with new images
client = Client()

# Create form data with images
files = {
    'images': [create_test_image('image1.png'), create_test_image('image2.png')],
}

# This is what the FormData would look like
from django.http import QueryDict
from urllib.parse import urlencode
import urllib.parse

# Simulate the form data that JavaScript would send
post_data = {
    'product_name': product.product_name,
    'category_name': product.category_name.id,
    'brand': product.brand.id if product.brand else '',
    'description': product.description or '',
    'price': str(product.price),
    'stock': str(product.stock),
}

# Prepare the files the way JavaScript FormData would
test_files = {
    'images': [create_test_image('test1.png'), create_test_image('test2.png')],
}

response = client.post(
    f'/update_product/{product.id}/',
    data=post_data,
    files=test_files
)

print(f"\nResponse: {response.status_code}")
print(f"Content: {response.content.decode()}")

# Check if images were created
product.refresh_from_db()
print(f"\nProduct images after update: {product.images.count()}")
for img in product.images.all():
    print(f"  - {img.product_image.name}")
