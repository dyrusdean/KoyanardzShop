import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

# Find the product from the screenshot
p = Product.objects.filter(model_3d__contains='Meshy_AI_Gaming_Setup_Collecti_0109062910').first()

if p:
    print(f"Product: {p.product_name}")
    print(f"ID: {p.id}")
    print(f"Price: {p.price}")
    print(f"Stock: {p.stock}")
    print(f"Model 3D: {p.model_3d.name if p.model_3d else 'None'}")
    print(f"Images count: {p.images.count()}")
    for img in p.images.all():
        print(f"  - {img.product_image.name}")
else:
    print("Product not found")
