#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()
from app.models import Product

print("PRODUCT IMAGE FIELD VALUES IN DATABASE:")
for p in Product.objects.filter(image__isnull=False)[:15]:
    print(f'Product {p.id}: image = "{p.image}"')
