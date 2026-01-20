import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product

# Get all unique component types
component_types = Product.objects.values_list('component_type', flat=True).distinct()
print("Existing Component Types in Database:")
for ct in sorted(component_types):
    count = Product.objects.filter(component_type=ct, stock__gt=0).count()
    print(f"  - {ct}: {count} items in stock")

# Check if motherboards exist
motherboards = Product.objects.filter(component_type__icontains='motherboard', stock__gt=0)
print(f"\nMotherboards found (icontains 'motherboard'): {motherboards.count()}")
for mb in motherboards[:3]:
    print(f"  - {mb.product_name} (component_type: {mb.component_type})")

# Check what "Computer Sets" are
computer_sets = Product.objects.filter(product_name__icontains='computer set', stock__gt=0)
print(f"\nComputer Sets found: {computer_sets.count()}")
for cs in computer_sets[:3]:
    print(f"  - {cs.product_name} (component_type: {cs.component_type}, category: {cs.category_name})")
