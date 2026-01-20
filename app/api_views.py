from django.shortcuts import get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Product
import requests
import os
import json
import logging
import jwt
import io
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def api_serve_3d_model(request, product_id):
    """
    Serve 3D model file from local storage with proper CORS headers.
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if not product.model_3d:
            return JsonResponse({'error': '3D model not found'}, status=404)
        
        logger.info(f"Serving 3D model for product {product_id}: {product.model_3d.name}")
        
        try:
            # Read file from local storage
            file_content = product.model_3d.read()
            
            # Create response with file content
            response = HttpResponse(file_content, content_type='model/gltf-binary')
            
            # Add CORS headers to allow browser to load the model
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Range'
            
            # Add cache headers for better performance
            response['Cache-Control'] = 'public, max-age=2592000'
            response['Content-Disposition'] = f'inline; filename="{product.model_3d.name}"'
            response['Content-Length'] = len(file_content)
            
            logger.info(f"✓ Successfully served 3D model: {product.model_3d.name} ({len(file_content)} bytes)")
            return response
            
        except Exception as e:
            logger.error(f"Error serving 3D model: {e}")
            return JsonResponse({'error': f'Failed to load model: {str(e)}'}, status=500)
    
    except Exception as e:
        logger.error(f"Error in model serving endpoint: {e}")
        return JsonResponse({'error': 'Model not found'}, status=404)

@require_http_methods(["GET"])
def api_product_3d_model(request, product_id):
    """
    API endpoint to get product 3D model and details
    Returns: {
        "success": true/false,
        "product_id": id,
        "product_name": name,
        "model_url": "/api/product/{id}/model-3d/",
        "description": "...",
        "price": 0.00,
        "brand": "...",
        "has_model": true/false
    }
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        model_url = None
        has_model = False
        
        if product.model_3d:
            # Use the proxy endpoint instead of direct B2 URL for CORS support
            model_url = request.build_absolute_uri(f'/api/product/{product.id}/model-3d/')
            has_model = True
        
        return JsonResponse({
            "success": True,
            "product_id": product.id,
            "product_name": product.product_name,
            "model_url": model_url,
            "description": product.description or "",
            "price": str(product.price),
            "brand": product.brand.brand if product.brand else "Unknown",
            "has_model": has_model,
            "component_type": product.component_type,
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)

@require_http_methods(["GET"])
def api_search_products_with_3d(request):
    """
    Search products that have 3D models
    Query params:
    - q: search query
    - component: filter by component type
    - limit: max results (default 50)
    """
    search_query = request.GET.get('q', '')
    component = request.GET.get('component', '')
    limit = int(request.GET.get('limit', 50))
    
    # Enforce max limit to prevent memory issues
    limit = min(limit, 100)
    
    products = Product.objects.filter(model_3d__isnull=False).exclude(model_3d='').select_related('brand', 'category_name')
    
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if component:
        products = products.filter(component_type=component)
    
    results = []
    for p in products[:limit]:
        results.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": str(p.price),
            "brand": p.brand.brand if p.brand else "Unknown",
            "component_type": p.component_type,
            "description": p.description or "",
            "has_model": True,
            "model_url": f'/api/product/{p.id}/model-3d/' if p.model_3d else None,
        })
    
    return JsonResponse({
        "success": True,
        "products": results,
        "total": len(results)
    })


@require_http_methods(["GET"])
def api_get_all_products(request):
    """
    Get all products with full details for chatbot recommendations
    Query params:
    - component: filter by component type (cpu, gpu, ram, etc.)
    - limit: max results (default 100, max 250)
    - search: search by product name
    """
    search_query = request.GET.get('search', '')
    component = request.GET.get('component', '')
    limit = int(request.GET.get('limit', 100))
    
    # Enforce max limit to prevent memory exhaustion
    limit = min(limit, 250)
    
    products = Product.objects.all().select_related('brand', 'category_name')
    
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if component:
        products = products.filter(component_type=component)
    
    results = []
    for p in products[:limit]:
        # Safely get image URL
        image_url = None
        if p.has_valid_image():
            try:
                image_url = p.image.url
            except (ValueError, AttributeError):
                image_url = None
        
        results.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": str(p.price),
            "brand": p.brand.brand if p.brand else "Unknown",
            "component_type": p.component_type,
            "description": p.description or "",
            "stock": p.stock,
            "category": p.category_name.category_name if p.category_name else "Unknown",
            "has_3d_model": bool(p.model_3d),
            "image_url": image_url,
        })
    
    return JsonResponse({
        "success": True,
        "products": results,
        "total": len(results)
    })


@api_view(['GET'])
def botpress_test(request):
    """
    Test endpoint - deprecated (Botpress removed)
    """
    return Response({'success': False, 'error': 'Botpress integration has been removed'}, status=410)


@require_http_methods(["GET"])
def api_gemini_system_prompt(request):
    """
    API endpoint to get the Gemini AI system prompt
    Returns the system instructions that guide the AI's behavior
    """
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), 'gemini_system_prompt.txt')
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            return JsonResponse({
                'success': True,
                'prompt': prompt_content
            })
        else:
            logger.warning(f"System prompt file not found: {prompt_path}")
            return JsonResponse({
                'success': False,
                'error': 'System prompt file not found'
            }, status=404)
    
    except Exception as e:
        logger.error(f"Error loading system prompt: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_products_recommend(request):
    """
    API endpoint for product recommendations
    Chatbot uses this to search and recommend products from store inventory
    Supports category parameter for strict category filtering
    """
    try:
        from .models import Product
        from django.db.models import Q
        
        query = request.GET.get('query', '').strip()
        category = request.GET.get('category', '').strip()
        max_price = request.GET.get('max_price')
        max_results = int(request.GET.get('max_results', 6))
        
        products_list = []
        
        # If category parameter is provided, search by category
        if category:
            try:
                category_lower = category.lower()
                
                # Create flexible search query using Q objects
                # This allows multiple search terms to work
                search_query = Q()
                
                # Add the main category search
                search_query |= Q(category_name__category_name__icontains=category_lower)
                
                # Add aliases for common component names
                if 'gpu' in category_lower or 'graphic' in category_lower or 'video card' in category_lower:
                    # Search for GPU, graphics card, or any variant
                    search_query |= Q(category_name__category_name__icontains='gpu')
                    search_query |= Q(category_name__category_name__icontains='graphics')
                    search_query |= Q(category_name__category_name__icontains='card')
                    search_query |= Q(product_name__icontains='graphics')
                    search_query |= Q(product_name__icontains='gpu')
                
                # Strategy 1: Try category_name match with flexible search
                products_list = list(Product.objects.filter(
                    Q(stock__gt=0) & search_query
                ).select_related('brand', 'category_name')[:max_results])
                
                # Strategy 2: If no results, try product name (case-insensitive)
                if not products_list:
                    products_list = list(Product.objects.filter(
                        stock__gt=0,
                        product_name__icontains=category
                    ).select_related('brand', 'category_name')[:max_results])
                
                # Apply price filter if results found
                if products_list and max_price:
                    try:
                        max_price_val = float(max_price)
                        products_list = [p for p in products_list if p.price <= max_price_val]
                    except:
                        pass
                
                # Format and return results
                if products_list:
                    products_data = []
                    for product in products_list:
                        brand_name = 'Unknown'
                        if product.brand:
                            brand_name = product.brand.brand if hasattr(product.brand, 'brand') else str(product.brand)
                        
                        category_name = 'Unknown'
                        if product.category_name:
                            category_name = product.category_name.category_name
                        
                        # Safely get image URL
                        image_url = '/static/images/placeholder.png'
                        if product.has_valid_image():
                            try:
                                image_url = product.image.url
                            except (ValueError, AttributeError):
                                image_url = '/static/images/placeholder.png'
                        
                        products_data.append({
                            'id': product.id,
                            'name': product.product_name,
                            'brand': brand_name,
                            'price': float(product.price),
                            'category': category_name,
                            'image_url': image_url,
                            'description': product.description or '',
                            'model_3d': f'/api/product/{product.id}/model-3d/' if product.model_3d else None
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'count': len(products_data),
                        'products': products_data
                    })
            except Exception as cat_error:
                logger.error(f"Category filter error: {str(cat_error)}")
                pass
        
        # Fall back to query parameter search if no category or no results
        if not query and not products_list:
            return JsonResponse({
                'success': True,
                'count': 0,
                'products': []
            })
        
        if query:
            # Create flexible search query using Q objects
            search_query = Q()
            
            # Add the main query search
            search_query |= Q(category_name__category_name__icontains=query)
            
            # Add special aliases for common components
            if 'gpu' in query.lower() or 'graphic' in query.lower() or 'video' in query.lower():
                # Graphics card search - find any variant
                search_query |= Q(category_name__category_name__icontains='gpu')
                search_query |= Q(category_name__category_name__icontains='graphics')
                search_query |= Q(product_name__icontains='graphics')
                search_query |= Q(product_name__icontains='gpu')
            
            # Try category and product name search first
            try:
                category_products = Product.objects.filter(
                    Q(stock__gt=0) & search_query
                ).select_related('brand', 'category_name')
                
                if category_products.exists():
                    # Apply price filter
                    if max_price:
                        try:
                            max_price_val = float(max_price)
                            category_products = category_products.filter(price__lte=max_price_val)
                        except:
                            pass
                    
                    products_list = list(category_products[:max_results])
            except Exception as cat_error:
                logger.error(f"Category search error: {str(cat_error)}")
                pass
            
            # If no category results, try product name search
            if not products_list:
                try:
                    name_products = Product.objects.filter(
                        stock__gt=0,
                        product_name__icontains=query
                    ).select_related('brand', 'category_name')
                    
                    if name_products.exists():
                        # Apply price filter
                        if max_price:
                            try:
                                max_price_val = float(max_price)
                                name_products = name_products.filter(price__lte=max_price_val)
                            except:
                                pass
                        
                        products_list = list(name_products[:max_results])
                except Exception as name_error:
                    logger.error(f"Product name search error: {str(name_error)}")
                    pass
            
            # If still no results, try brand search
            if not products_list:
                try:
                    brand_products = Product.objects.filter(
                        stock__gt=0,
                        brand__brand__icontains=query
                    ).select_related('brand', 'category_name')
                    
                    if brand_products.exists():
                        # Apply price filter
                        if max_price:
                            try:
                                max_price_val = float(max_price)
                                brand_products = brand_products.filter(price__lte=max_price_val)
                            except:
                                pass
                        
                        products_list = list(brand_products[:max_results])
                except Exception as brand_error:
                    logger.error(f"Brand search error: {str(brand_error)}")
                    pass
        
        # Format results
        products_data = []
        for product in products_list:
            try:
                cat_name = 'Unknown'
                if product.category_name:
                    cat_name = product.category_name.category_name or 'Unknown'
                
                brand_name = 'Unknown'
                if product.brand:
                    brand_name = product.brand.brand or 'Unknown'
                
                image_url = '/static/images/placeholder.png'
                if product.has_valid_image():
                    try:
                        image_url = product.image.url
                    except (ValueError, AttributeError):
                        image_url = '/static/images/placeholder.png'
                
                model_3d_url = None
                if product.model_3d:
                    model_3d_url = f'/api/product/{product.id}/model-3d/'
                
                product_dict = {
                    'id': product.id,
                    'name': product.product_name or 'Unnamed',
                    'category': cat_name,
                    'price': float(product.price or 0),
                    'description': product.description or '',
                    'image_url': image_url,
                    'brand': brand_name,
                    'model_3d': model_3d_url
                }
                products_data.append(product_dict)
            except Exception as item_error:
                logger.error(f"Error formatting product: {str(item_error)}")
                continue
        
        return JsonResponse({
            'success': True,
            'count': len(products_data),
            'products': products_data
        })
    
    except Exception as e:
        logger.error(f"Error in product recommendations: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': True,
            'count': 0,
            'products': []
        })


@require_http_methods(["GET"])
def api_available_categories(request):
    """
    Returns list of all available product categories from database
    Used by chatbot to know what categories actually exist
    """
    try:
        from .models import Category
        
        # Get all categories
        categories = Category.objects.all().values_list('category_name', flat=True).distinct()
        categories_list = sorted(list(categories))
        
        return JsonResponse({
            'success': True,
            'categories': categories_list,
            'count': len(categories_list)
        })
    
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_store_info(request):
    """
    Returns store information for chatbot to use
    Includes product categories, component types, and general store info
    """
    try:
        from .models import Category, Product
        from django.db.models import Min, Max
        
        # Get all available categories with stock
        categories_with_stock = Product.objects.filter(
            stock__gt=0
        ).values_list('category_name__category_name', flat=True).distinct()
        categories_list = sorted(list(set([c for c in categories_with_stock if c])))
        
        # Get price range
        price_data = Product.objects.filter(stock__gt=0).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        min_price = float(price_data['min_price'] or 0)
        max_price = float(price_data['max_price'] or 0)
        
        # Count total products in stock
        total_products = Product.objects.filter(stock__gt=0).count()
        
        return JsonResponse({
            'success': True,
            'categories': categories_list,
            'price_range': {
                'min': min_price,
                'max': max_price
            },
            'total_products_in_stock': total_products
        })
    
    except Exception as e:
        logger.error(f"Error fetching store info: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def api_save_chat_conversation(request):
    """
    Save chat conversation and build state for logged-in users or anonymous users
    Each user (logged-in or not) has their own separate conversation
    POST data: {
        "session_id": "unique-session-id",
        "messages": [{"role": "user/model", "content": "..."}],
        "build_state": { "selectedComponents": {...}, ... }  (optional)
    }
    """
    try:
        from .models import ChatConversation
        
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        messages = data.get('messages', [])
        build_state = data.get('build_state', {})
        
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id required'}, status=400)
        
        # Validate session ID format
        if request.user.is_authenticated:
            # For logged-in users, session_id should be user-{id}-chat
            expected_session = f'user-{request.user.id}-chat'
            if session_id != expected_session:
                return JsonResponse({'success': False, 'error': 'Invalid session for logged-in user'}, status=403)
        else:
            # For anonymous users, session_id should start with 'anon-'
            if not session_id.startswith('anon-'):
                return JsonResponse({'success': False, 'error': 'Invalid session for anonymous user'}, status=403)
        
        # Get or create conversation - each user gets their own
        conversation, created = ChatConversation.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )
        
        # Verify user ownership (for logged-in users)
        if request.user.is_authenticated and conversation.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized: Cannot modify another user\'s conversation'}, status=403)
        
        # Update messages and build state
        conversation.messages = messages
        if build_state:
            conversation.build_state = build_state
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': 'Conversation saved'
        })
    
    except Exception as e:
        logger.error(f"Error saving chat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_load_chat_conversation(request):
    """
    Load chat conversation for logged-in users or by session_id
    GET params: session_id (required)
    """
    try:
        from .models import ChatConversation
        
        session_id = request.GET.get('session_id', '')
        
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id required'}, status=400)
        
        # Try to get conversation
        conversation = ChatConversation.objects.filter(session_id=session_id).first()
        
        if not conversation:
            # No conversation found, return empty
            return JsonResponse({
                'success': True,
                'messages': [],
                'found': False
            })
        
        return JsonResponse({
            'success': True,
            'messages': conversation.messages,
            'found': True,
            'conversation_id': conversation.id
        })
    
    except Exception as e:
        logger.error(f"Error loading chat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def api_delete_chat_conversation(request):
    """
    Delete chat conversation
    Each user can only delete their own conversation
    POST data: {
        "session_id": "unique-session-id"
    }
    """
    try:
        from .models import ChatConversation
        
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id required'}, status=400)
        
        # Validate session ID format
        if request.user.is_authenticated:
            # For logged-in users, session_id should be user-{id}-chat
            expected_session = f'user-{request.user.id}-chat'
            if session_id != expected_session:
                return JsonResponse({'success': False, 'error': 'Invalid session for logged-in user'}, status=403)
        else:
            # For anonymous users, session_id should start with 'anon-'
            if not session_id.startswith('anon-'):
                return JsonResponse({'success': False, 'error': 'Invalid session for anonymous user'}, status=403)
        
        # Get conversation first to verify ownership
        conversation = ChatConversation.objects.filter(session_id=session_id).first()
        
        if not conversation:
            return JsonResponse({'success': False, 'error': 'Conversation not found'}, status=404)
        
        # Verify user ownership (for logged-in users)
        if request.user.is_authenticated and conversation.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized: Cannot delete another user\'s conversation'}, status=403)
        
        # Delete conversation
        conversation.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation deleted'
        })
    
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Firebase Email Verification
@api_view(['POST'])
def firebase_signup_verify(request):
    """
    Verify Firebase signup and create Django user
    Expects: {
        "uid": "firebase_user_id",
        "email": "user@example.com",
        "email_verified": true,
        "display_name": "User Name" (optional)
    }
    """
    try:
        from .firebase_auth import get_or_create_user_from_firebase
        from django.contrib.auth import get_user_model, login
        
        data = request.data
        
        # Validate required fields
        if not data.get('email'):
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=400)
        
        if not data.get('email_verified'):
            return Response({
                'success': False,
                'message': 'Email must be verified'
            }, status=400)
        
        firebase_uid = data.get('uid', '')
        email = data.get('email')
        display_name = data.get('display_name', '')
        
        # Get or create Django user
        user, created = get_or_create_user_from_firebase(firebase_uid, email, display_name)
        
        # Login the user
        from django.contrib.auth.backends import ModelBackend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return Response({
            'success': True,
            'message': 'Email verified successfully!' if created else 'Welcome back!',
            'created': created,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff
            }
        })
        
    except Exception as e:
        logger.error(f"Firebase signup verification error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Verification failed. Please try again.',
            'error': str(e)
        }, status=500)
