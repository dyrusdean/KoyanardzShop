import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

# Check products from the screenshot
product_ids = [20, 21, 26, 27, 28]

for prod_id in product_ids:
    p = Product.objects.get(id=prod_id)
    print(f"Product {prod_id}: {p.product_name}")
    print(f"  - Main image field: {p.image.name if p.image else 'None'}")
    print(f"  - ProductImage records: {p.images.count()}")
    print()
