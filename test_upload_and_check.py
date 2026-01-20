import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

# Get a product without images
product = Product.objects.filter(images__isnull=True).first()

if product:
    print(f"Testing with product: {product.product_name} (ID: {product.id})")
    print(f"Current images: {product.images.count()}")
    
    # Create test images
    for i in range(3):
        img = Image.new('RGB', (100, 100), color=(i*80, i*80, i*80))
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        ProductImage.objects.create(
            product=product,
            product_image=SimpleUploadedFile(f'test{i}.png', img_io.read(), content_type='image/png'),
            order=i
        )
    
    # Refresh and check
    product.refresh_from_db()
    print(f"Images after creation: {product.images.count()}")
    for img in product.images.all():
        print(f"  - {img.product_image.name}")
    
    # Now test the API
    from django.test import RequestFactory
    from app.views import get_product_details
    import json
    
    factory = RequestFactory()
    request = factory.get(f'/api/product/{product.id}/')
    response = get_product_details(request, product.id)
    
    print(f"\nAPI Response:")
    data = json.loads(response.content)
    print(f"Images returned: {len(data.get('images', []))}")
    print(f"Response: {json.dumps(data, indent=2)}")
else:
    print("No products without images found")
