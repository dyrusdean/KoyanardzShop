#!/usr/bin/env python
"""
Verification script for 3D model proxy endpoint fix
"""

def check_template_fix():
    """Verify product_item.html uses proxy URL"""
    template_path = r'c:\Users\eborg\OneDrive\Documents\GitHub\Koyanardzshop\app\templates\app\buying\product_item.html'
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the proxy URL format
    if "/api/product/{{ produkto.id }}/model-3d/" in content:
        print("✓ product_item.html correctly uses proxy endpoint: /api/product/{{ produkto.id }}/model-3d/")
        return True
    else:
        print("✗ product_item.html NOT using proxy endpoint")
        return False

def check_api_endpoint_fix():
    """Verify api_views.py has the proxy endpoint"""
    api_path = r'c:\Users\eborg\OneDrive\Documents\GitHub\Koyanardzshop\app\api_views.py'
    
    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def api_serve_3d_model(request, product_id):' in content:
        print("✓ api_views.py has api_serve_3d_model function defined")
        
        # Check for CORS headers
        if "Access-Control-Allow-Origin" in content:
            print("✓ CORS headers are set in proxy endpoint")
            return True
    
    return False

def check_url_routing():
    """Verify urls.py has the route for proxy endpoint"""
    urls_path = r'c:\Users\eborg\OneDrive\Documents\GitHub\Koyanardzshop\app\urls.py'
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "api/product/<int:product_id>/model-3d/" in content and "api_serve_3d_model" in content:
        print("✓ app/urls.py has route for /api/product/<product_id>/model-3d/ proxy endpoint")
        return True
    else:
        print("✗ app/urls.py missing route for proxy endpoint")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("3D MODEL PROXY ENDPOINT VERIFICATION")
    print("=" * 70 + "\n")
    
    checks = [
        ("Template Fix", check_template_fix),
        ("API Endpoint", check_api_endpoint_fix),
        ("URL Routing", check_url_routing),
    ]
    
    all_passed = True
    for name, check in checks:
        print(f"\nChecking {name}...")
        if not check():
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - 3D model proxy endpoint is properly configured")
        print("\nTo test the fix:")
        print("1. Navigate to http://localhost:8000/product_item/197/")
        print("2. Open browser DevTools (F12)")
        print("3. Check Network tab for request to /api/product/197/model-3d/")
        print("4. Should see 200 OK response with CORS headers")
    else:
        print("✗ SOME CHECKS FAILED - Please review the errors above")
    print("=" * 70)
