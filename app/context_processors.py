from .models import Product, Favorite

def favorites_context(request):
    """Populate context with favorite products from database (auth) or session (anonymous)."""
    favorites_list = []
    products = Product.objects.none()
    
    # For authenticated users, get from database
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('favorite_product_id', flat=True)
        favorites_list = [str(f) for f in favorites]
        products = Product.objects.filter(id__in=favorites)
    else:
        # For anonymous users, get from session
        favorites_list = request.session.get('favorites', [])
        try:
            favorite_ids = [int(fav_id) for fav_id in favorites_list if fav_id]
        except (ValueError, TypeError):
            favorite_ids = []
        
        products = Product.objects.filter(id__in=favorite_ids) if favorite_ids else Product.objects.none()
    
    # Filter out products without valid images
    valid_products = []
    for p in products:
        if p.has_valid_image():
            valid_products.append(p)
    
    # Get cart count from session
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    
    return {
        'products_favorite': valid_products,
        'favorites': favorites_list,  # Also provide the raw list for template checks
        'cart_count': cart_count
    }
