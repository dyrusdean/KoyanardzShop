#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

p = Product.objects.get(id=86)
print(f'Product: {p.product_name}')
print(f'model_3d field: "{p.model_3d}"')
print(f'model_3d.name: "{p.model_3d.name if p.model_3d else "NONE"}"')
print(f'model_3d.url: "{p.model_3d.url if p.model_3d else "NONE"}"')
print(f'model_3d bool: {bool(p.model_3d)}')
print(f'model_3d type: {type(p.model_3d)}')
