import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

# Count products without images
total_products = Product.objects.count()
products_without_images = Product.objects.exclude(images__isnull=False).distinct().count()
products_with_images = Product.objects.filter(images__isnull=False).distinct().count()

print(f"Total products: {total_products}")
print(f"Products WITH images: {products_with_images}")
print(f"Products WITHOUT images: {products_without_images}")

print("\nProducts without images:")
for p in Product.objects.exclude(images__isnull=False).distinct()[:10]:
    print(f"  - ID {p.id}: {p.product_name}")
