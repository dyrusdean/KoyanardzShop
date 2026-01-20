import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

# Get first product
product = Product.objects.first()

if product:
    print(f"Product: {product.product_name} (ID: {product.id})")
    print(f"Current images: {product.images.count()}")
    
    # Delete existing images
    product.images.all().delete()
    print(f"Images after deletion: {product.images.count()}")
    
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    # Create ProductImage record
    test_image = ProductImage.objects.create(
        product=product,
        product_image=ContentFile(img_io.read(), name='test.png'),
        order=0
    )
    print(f"Created test image: {test_image.id}")
    print(f"Images after creation: {product.images.count()}")
    print(f"Image URL: {test_image.product_image.url}")
    
    # Verify it was saved
    product.refresh_from_db()
    print(f"Images after refresh: {product.images.count()}")
