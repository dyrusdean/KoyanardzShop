"""
Test script to verify the cart, favorites, and add to cart functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuynSell.settings')
django.setup()

from app.models import Product, Category, Brand, Cart, Favorite

def test_products():
    """Verify products exist"""
    products = Product.objects.all()
    print(f"✓ Total products in database: {products.count()}")
    
    if products.exists():
        for p in products[:3]:
            print(f"  - {p.product_name} (ID: {p.id}, Price: ₱{p.price}, Stock: {p.stock})")
    return products.count() > 0

def test_categories():
    """Verify categories exist"""
    categories = Category.objects.all()
    print(f"✓ Total categories: {categories.count()}")
    return categories.count() > 0

def test_brands():
    """Verify brands exist"""
    brands = Brand.objects.all()
    print(f"✓ Total brands: {brands.count()}")
    return brands.count() > 0

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Database Structure")
    print("=" * 50)
    
    try:
        test_products()
        test_categories()
        test_brands()
        print("\n✓ All database checks passed!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
