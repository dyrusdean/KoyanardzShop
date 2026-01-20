from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView
from .models import OtpToken, Category, Brand, Product, ProductImage, ProductReview, Appointment, AppointmentProduct, Selling, Favorite, ProductVariation
from .forms import RegisterForm, LoginForm, ProfileForm, ProfileUpdateForm, AddCategory, AddBrand, Add, AddVariantForm, ProductReviewForm, AppointmentForm, SellingForm, CustomPasswordResetForm, CustomSetPasswordForm
from .serializers import ProductSerializer
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from datetime import date, time, datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .email_utils import send_email
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum, F
from django.db import models
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os, json
import random
import urllib.parse

def filter_products_with_valid_images(products_queryset):
    """Filter products to only include those with valid image files"""
    valid_products = []
    for p in products_queryset:
        if p.has_valid_image():
            valid_products.append(p)
    return valid_products

def product_list(request):
    component = request.GET.get('component')
    qs = Product.objects.all()

    if component:
        qs = qs.filter(component__iexact=component)

    return JsonResponse({
        "results": list(qs.values())
    })

def get_products(request):
    component = request.GET.get("component")
    products = Product.objects.filter(category=component, stock__gt=0)
    data = [
        {
            "id": p.id,
            "name": p.product_name,
            "price": float(p.price),
            "thumbnail": p.thumbnail.url if p.thumbnail else "",
            "glb": f"/static/images/3D/{p.glb_file}"
        } for p in products
    ]
    return JsonResponse({"products": data})

def save_appointment(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Post required'}, status=400)
    
    data = json.loads(request.body.decode("utf-8"))

    Appointment.objects.create(
        first_name = data.get("first_name"),
        last_name = data.get("last_name"),
        contact = data.get("contact"),
        email = data.get("email"),
        date = data.get("date"),
        time = data.get("time")
    )
    return JsonResponse({"status:" "success"})

def model_viewer(request):
    parts = request.GET.get('parts', '')
    models = [m for m in parts.split(',') if m]
    models = [f"/static/images/3D/{m}" for m in models]
    return render(request, 'app/buying/model_viewer.html', {'models': models})

def ai3d_test(request):
    """Test page for Botpress AI 3D model generation"""
    return render(request, 'ai3dtest.html')


#ADMIN

def addproduct(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all().order_by('brand')
    product_form = Add()
    category_form = AddCategory()
    brand_form = AddBrand()
    variant_form = AddVariantForm()
    
    # Filtering logic - initialize filter variables
    category_filter = request.GET.get('category', '').strip()
    brand_filter = request.GET.get('brand', '').strip()
    search_query = request.GET.get('search', '').strip()
    
    # Apply filters only if they have actual values
    if category_filter and category_filter != '':
        products = products.filter(category_name_id=category_filter)
    
    if brand_filter and brand_filter != '':
        products = products.filter(brand_id=brand_filter)
    
    if search_query and search_query != '':
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if request.method == 'POST':
        if 'add_product' in request.POST:
            product_form = Add(request.POST, request.FILES)
            if product_form.is_valid():
                new_product = product_form.save()
                images = request.FILES.getlist('images')

                for idx, image in enumerate(images):
                    ProductImage.objects.create(product=new_product, product_image=image, order=idx)
                return redirect('admin_product')
        elif 'add_category' in request.POST:
            category_form = AddCategory(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect('admin_product')
        elif 'add_brand' in request.POST:
            brand_form = AddBrand(request.POST)
            if brand_form.is_valid():
                brand_form.save()
                return redirect('admin_product')
        elif 'add_variant' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            variant_form = AddVariantForm(request.POST, request.FILES)

            if variant_form.is_valid():
                new_variant = variant_form.save(commit=False)
                new_variant.product = product
                new_variant.save()
                return redirect('admin_product')

    return render(request, 'app/admin/admin_product.html', {
        'products': products,
        'form': product_form,
        'category_form': category_form,
        'categories': categories,
        'brand_form': brand_form,
        'brands': brands,
        'variant_form': variant_form,
        'category_filter': category_filter,
        'brand_filter': brand_filter,
        'search_query': search_query
    })

# AJAX API Endpoints for Admin Modals

@csrf_exempt
def add_product_ajax(request):
    """AJAX endpoint for adding category, brand, or product"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        form_type = request.POST.get('form_type', '')
        
        if form_type == 'category':
            # Add new category
            category_name = request.POST.get('category_name', '').strip()
            if not category_name:
                return JsonResponse({'status': 'error', 'message': 'Category name is required'})
            
            from .models import Category
            Category.objects.get_or_create(category_name=category_name)
            return JsonResponse({'status': 'success', 'message': 'Category added successfully'})
        
        elif form_type == 'brand':
            # Add new brand
            brand_name = request.POST.get('brand', '').strip()
            if not brand_name:
                return JsonResponse({'status': 'error', 'message': 'Brand name is required'})
            
            from .models import Brand
            Brand.objects.get_or_create(brand=brand_name)
            return JsonResponse({'status': 'success', 'message': 'Brand added successfully'})
        
        elif form_type == 'product':
            # Add new product
            product_name = request.POST.get('product_name', '').strip()
            category_id = request.POST.get('category_name')
            brand_id = request.POST.get('brand')
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', '0')
            stock = request.POST.get('stock', '0')
            
            if not all([product_name, category_id, brand_id, price, stock]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
            
            from .models import Category, Brand
            from .utils import validate_3d_model_file, validate_image_file
            
            try:
                category = Category.objects.get(id=category_id)
                brand = Brand.objects.get(id=brand_id)
            except (Category.DoesNotExist, Brand.DoesNotExist):
                return JsonResponse({'status': 'error', 'message': 'Invalid category or brand'})
            
            # Validate 3D model file before processing
            if 'model_3d' in request.FILES:
                try:
                    validate_3d_model_file(request.FILES['model_3d'], max_size_mb=100)
                except ValidationError as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
            # Validate images before processing
            if 'images' in request.FILES:
                for image_file in request.FILES.getlist('images'):
                    try:
                        validate_image_file(image_file, max_size_mb=10)
                    except ValidationError as e:
                        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
            product = Product(
                product_name=product_name,
                category_name=category,
                brand=brand,
                description=description,
                price=float(price),
                stock=int(stock)
            )
            
            # Handle single image as main image (for backward compatibility)
            if 'image' in request.FILES:
                try:
                    validate_image_file(request.FILES['image'], max_size_mb=10)
                    product.image = request.FILES['image']
                except ValidationError as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
            # Handle 3D model upload (only one)
            if 'model_3d' in request.FILES:
                model_file = request.FILES['model_3d']
                logger.info(f"Adding 3D model: {model_file.name}")
                product.model_3d = model_file
            
            product.save()
            
            # Check where 3D model ended up
            if product.model_3d:
                logger.info(f"✓ Product {product.id} 3D model saved. URL: {product.model_3d.url}")
            
            # Handle multiple images
            if 'images' in request.FILES:
                image_list = request.FILES.getlist('images')
                logger.info(f"Adding {len(image_list)} images for product {product.id}")
                for idx, image_file in enumerate(image_list):
                    ProductImage.objects.create(
                        product=product,
                        product_image=image_file,
                        order=idx
                    )
                # Set the main product image to the first uploaded image
                first_product_image = product.images.first()
                if first_product_image and not product.image:
                    product.image = first_product_image.product_image
                    product.save()
            
            return JsonResponse({'status': 'success', 'message': 'Product added successfully'})
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form type'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def update_product_ajax(request, product_id):
    """AJAX endpoint for updating a product"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        from .utils import validate_3d_model_file, validate_image_file
        
        product = get_object_or_404(Product, id=product_id)
        
        # Validate 3D model file before processing
        if 'model_3d' in request.FILES:
            try:
                validate_3d_model_file(request.FILES['model_3d'], max_size_mb=100)
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        # Validate images before processing
        if 'images' in request.FILES:
            for image_file in request.FILES.getlist('images'):
                try:
                    validate_image_file(image_file, max_size_mb=10)
                except ValidationError as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        # Update fields
        if 'product_name' in request.POST:
            product.product_name = request.POST.get('product_name', '').strip()
        
        if 'category_name' in request.POST:
            category_id = request.POST.get('category_name')
            if category_id:
                from .models import Category
                product.category_name = get_object_or_404(Category, id=category_id)
        
        if 'brand' in request.POST:
            brand_id = request.POST.get('brand')
            if brand_id:
                from .models import Brand
                product.brand = get_object_or_404(Brand, id=brand_id)
        
        if 'description' in request.POST:
            product.description = request.POST.get('description', '').strip()
        
        if 'price' in request.POST:
            price = request.POST.get('price', '')
            if price:
                product.price = float(price)
        
        if 'stock' in request.POST:
            stock = request.POST.get('stock', '')
            if stock:
                product.stock = int(stock)
        
        # Handle image upload (single, for backward compatibility)
        if 'image' in request.FILES:
            try:
                validate_image_file(request.FILES['image'], max_size_mb=10)
                product.image = request.FILES['image']
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        # Handle 3D model upload (only one)
        if 'model_3d' in request.FILES:
            product.model_3d = request.FILES['model_3d']
        
        product.save()
        
        # Handle multiple images
        if 'images' in request.FILES:
            # Delete old images and add new ones
            product.images.all().delete()
            for idx, image_file in enumerate(request.FILES.getlist('images')):
                ProductImage.objects.create(
                    product=product,
                    product_image=image_file,
                    order=idx
                )
            # Set the main product image to the first uploaded image
            first_product_image = product.images.first()
            if first_product_image:
                product.image = first_product_image.product_image
                product.save()
        
        return JsonResponse({'status': 'success', 'message': 'Product updated successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def add_product_variant_ajax(request, product_id):
    """AJAX endpoint for adding a variant to a product"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        from .models import ProductVariation
        product = get_object_or_404(Product, id=product_id)
        
        # Get variant data from request
        product_variation = request.POST.get('product_variation', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '')
        stock = request.POST.get('stock', '')
        
        # Validate required fields
        if not product_variation:
            return JsonResponse({'status': 'error', 'message': 'Variant name is required'})
        if not price:
            return JsonResponse({'status': 'error', 'message': 'Price is required'})
        if not stock:
            return JsonResponse({'status': 'error', 'message': 'Stock is required'})
        
        # Create the variant
        variant = ProductVariation.objects.create(
            product=product,
            product_variation=product_variation,
            description=description,
            price=float(price),
            stock=int(stock)
        )
        
        # Handle image upload if provided
        if 'image' in request.FILES:
            variant.image = request.FILES['image']
            variant.save()
        
        return JsonResponse({'status': 'success', 'message': 'Variant added successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def delete_product_ajax(request, product_id):
    """AJAX endpoint for deleting a product"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'status': 'success', 'message': 'Product deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def get_product_details(request, product_id):
    """AJAX endpoint for getting product details including images and 3D model"""
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Get all images for the product
        images = []
        
        # Add main product image if it exists
        if product.image and product.image.name:
            images.append({
                'url': product.image.url,
                'id': 0,  # Use 0 as a special ID for the main image
                'is_main': True
            })
        
        # Add ProductImage records
        for img in product.images.all():
            images.append({
                'url': img.product_image.url,
                'id': img.id,
                'is_main': False
            })
        
        # Get 3D model filename if exists
        model_3d = None
        if product.model_3d and product.model_3d.name:
            model_3d = product.model_3d.name.split('/')[-1]  # Get just the filename
        
        return JsonResponse({
            'status': 'success',
            'images': images,
            'model_3d': model_3d
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def update_category(request, category_id):
    """AJAX endpoint for updating a category"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        category = get_object_or_404(Category, id=category_id)
        
        category_name = request.POST.get('category_name', '').strip()
        if not category_name:
            return JsonResponse({'status': 'error', 'message': 'Category name is required'})
        
        category.category_name = category_name
        category.save()
        return JsonResponse({'status': 'success', 'message': 'Category updated successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def delete_category(request, category_id):
    """AJAX endpoint for deleting a category"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'status': 'success', 'message': 'Category deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def update_brand(request, brand_id):
    """AJAX endpoint for updating a brand"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        brand = get_object_or_404(Brand, id=brand_id)
        
        brand_name = request.POST.get('brand', '').strip()
        if not brand_name:
            return JsonResponse({'status': 'error', 'message': 'Brand name is required'})
        
        brand.brand = brand_name
        brand.save()
        return JsonResponse({'status': 'success', 'message': 'Brand updated successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def delete_brand(request, brand_id):
    """AJAX endpoint for deleting a brand"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        brand = get_object_or_404(Brand, id=brand_id)
        brand.delete()
        return JsonResponse({'status': 'success', 'message': 'Brand deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def update_product(request):
    if request.method == 'POST':
        data = request.POST
        product = get_object_or_404(Product, id=data['id'])
        product.product_name = data['product_name']
        product.stock = data['stock']
        product.price = data['price']
        
        # Handle model_3d file upload
        if 'model_3d' in request.FILES:
            product.model_3d = request.FILES['model_3d']
        
        product.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_protect 
def delete_products(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        Product.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

#END ADMIN

#REGISTER & LOGIN

@ensure_csrf_cookie
@csrf_protect
@ensure_csrf_cookie
def register(request):
    form = RegisterForm()
    otp_code = None 
    temp_email = None
    temp_username = None

    if request.method == 'POST':
        if 'otp_code' in request.POST: 
            # OTP Verification - only now create the account
            username = request.POST.get('username', '').strip()
            otp_code_input = request.POST.get('otp_code', '').strip()
            
            logger.info(f"OTP verification attempt for username: {username}, OTP input length: {len(otp_code_input)}")
            
            if not username or not otp_code_input:
                messages.error(request, "❌ Username and OTP code are required.")
                return redirect("register")
            
            try:
                user = get_user_model().objects.get(username=username)
                user_otp = OtpToken.objects.filter(user=user).last()
                
                logger.info(f"User found: {username}, has OTP: {user_otp is not None}")
                
                if user_otp:
                    logger.info(f"OTP stored code: '{user_otp.otp_code}' (len={len(str(user_otp.otp_code))})")
                    logger.info(f"OTP input code: '{otp_code_input}' (len={len(otp_code_input)})")
                    logger.info(f"OTP codes match: {str(user_otp.otp_code) == otp_code_input}")

                if user_otp and str(user_otp.otp_code) == otp_code_input:
                    logger.info(f"OTP code matches for {username}")
                    if user_otp.otp_expires_at > timezone.now():
                        # OTP verified! Activate the user
                        user.is_active = True
                        user.save()
                        logger.info(f"OTP verified for user: {username}")
                        
                        # Refresh user from database to ensure fresh state
                        user = get_user_model().objects.get(username=username)
                        
                        # Auto-login the user after OTP verification
                        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        logger.info(f"User {username} logged in after OTP verification")
                        logger.info(f"User is_active after login: {user.is_active}")
                        logger.info(f"Request user after login: {request.user}, is_authenticated: {request.user.is_authenticated}")
                        
                        # Delete the OTP token after successful verification
                        user_otp.delete()
                        
                        messages.success(request, "✓ Email verified! Welcome to Koya Nardz Shop!")
                        return redirect("home")
                    else:
                        logger.warning(f"OTP expired for user: {username}")
                        messages.error(request, "⏱ OTP expired. Please request a new code.")
                        otp = OtpToken.objects.filter(user=user).last()
                        if otp:
                            otp_code = otp.otp_code
                        # Keep the form with the user's data for resend
                        context = {
                            "form": RegisterForm(instance=user),
                            "otp_code": otp_code,
                        }
                        return render(request, "app/account/signup.html", context)
                else:
                    logger.warning(f"Invalid OTP code for user: {username}")
                    messages.error(request, "❌ Invalid OTP code. Please check and try again.")
                    otp = OtpToken.objects.filter(user=user).last()
                    if otp:
                        otp_code = otp.otp_code
                    # Keep the form with the user's data for retry
                    context = {
                        "form": RegisterForm(instance=user),
                        "otp_code": otp_code,
                    }
                    return render(request, "app/account/signup.html", context)
            except get_user_model().DoesNotExist:
                logger.error(f"User not found during OTP verification: {username}")
                messages.error(request, "❌ User not found. Please sign up again.")
                return redirect("register")

        else: 
            # Initial signup - just send OTP, don't create account yet
            form = RegisterForm(request.POST)
            logger.info(f"Signup form received. Is valid: {form.is_valid()}")
            if not form.is_valid():
                logger.warning(f"Form validation failed. Errors: {form.errors}")
            
            if form.is_valid():
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                logger.info(f"Form valid. Email: {email}, Username: {username}")
                
                # Check if user already exists (includes inactive users awaiting OTP verification)
                existing_user = get_user_model().objects.filter(username=username).first()
                if existing_user:
                    # If inactive user exists with active OTP, just show OTP screen
                    if not existing_user.is_active:
                        user_otp = OtpToken.objects.filter(user=existing_user).last()
                        if user_otp and user_otp.otp_expires_at > timezone.now():
                            logger.info(f"User {username} already in signup process, showing OTP screen")
                            otp_code = user_otp.otp_code
                            context = {
                                "form": RegisterForm(instance=existing_user),
                                "otp_code": otp_code,
                            }
                            return render(request, "app/account/signup.html", context)
                    messages.error(request, "❌ Username already exists.")
                    return redirect("register")
                
                existing_email = get_user_model().objects.filter(email=email).first()
                if existing_email:
                    # If inactive user exists with active OTP, just show OTP screen
                    if not existing_email.is_active:
                        user_otp = OtpToken.objects.filter(user=existing_email).last()
                        if user_otp and user_otp.otp_expires_at > timezone.now():
                            logger.info(f"Email {email} already in signup process, showing OTP screen")
                            otp_code = user_otp.otp_code
                            context = {
                                "form": RegisterForm(instance=existing_email),
                                "otp_code": otp_code,
                            }
                            return render(request, "app/account/signup.html", context)
                    messages.error(request, "❌ Email already registered.")
                    return redirect("register")
                
                # Create user but mark as INACTIVE until OTP is verified
                user = form.save(commit=False)
                user.is_active = False  # NOT ACTIVE UNTIL OTP VERIFIED
                user.set_password(password)
                user.save()
                logger.info(f"User created: {username}")
                
                # Delete any old OTP tokens for this user (in case of retries)
                OtpToken.objects.filter(user=user).delete()
                
                # Generate and send OTP (only one)
                otp = OtpToken.objects.create(
                    user=user,
                    otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
                )
                logger.info(f"OTP created: {otp.otp_code}")
                
                # Send OTP email
                subject = "Email Verification Code - Koya Nardz Shop"
                message = f"""
Dear {username},

Your OTP verification code is:
{otp.otp_code}

This code expires in 5 minutes.

If you didn't create this account, please ignore this email.

Best regards,
Koya Nardz Shop Team
                """
                
                try:
                    logger.info(f"Attempting to send OTP email to {email}")
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    logger.info(f"OTP email sent successfully to {email}")
                    otp_code = otp.otp_code
                    # Set session flag to indicate fresh OTP was just sent
                    request.session['fresh_otp_timestamp'] = timezone.now().timestamp()
                    request.session['fresh_otp_user'] = username
                    messages.success(request, "✉ Verification code sent! Check your email.")
                except Exception as e:
                    logger.exception(f"Failed to send OTP email to {email}: {str(e)}")
                    # Delete the user if email fails
                    user.delete()
                    # Don't expose technical error details to user
                    messages.error(request, "❌ Failed to send verification email. Please try again later or contact support.")
                    return redirect("register")

    context = {
        "form": form,
        "otp_code": otp_code,
        "is_fresh_otp": otp_code is not None,  # True only if we just created/sent an OTP in this request
    }
    return render(request, "app/account/signup.html", context)


@ensure_csrf_cookie
def resend_otp(request):
    """
    Resend OTP to user's email
    Handles cooldown and creates a new OTP token
    """
    if request.method == 'POST':
        user_email = request.POST.get("otp_email", "").strip()
        
        logger.info(f"Resend OTP request received for email: {user_email}")
        logger.debug(f"Request META: {request.META.get('CONTENT_TYPE')}")
        logger.debug(f"POST data: {list(request.POST.keys())}")
        
        # Check if a fresh OTP was sent very recently (within 90 seconds)
        fresh_otp_timestamp = request.session.get('fresh_otp_timestamp')
        fresh_otp_user = request.session.get('fresh_otp_user')
        
        if fresh_otp_timestamp and fresh_otp_user:
            time_since_fresh = timezone.now().timestamp() - fresh_otp_timestamp
            logger.info(f"Fresh OTP was sent {time_since_fresh}s ago for user {fresh_otp_user}")
            
            if time_since_fresh < 90:
                # Too soon - likely an accidental duplicate submission during initial signup
                logger.warning(f"Blocking resend_otp - fresh OTP sent only {time_since_fresh}s ago")
                seconds_remaining = int(90 - time_since_fresh)
                messages.warning(request, f"⏱ Please wait {seconds_remaining} seconds before requesting a new OTP")
                
                # Get existing OTP and return signup form
                try:
                    user = get_user_model().objects.get(email=user_email)
                    last_otp = OtpToken.objects.filter(user=user).order_by('-tp_created_at').first()
                    form = RegisterForm(instance=user)
                    context = {
                        "form": form,
                        "otp_code": last_otp.otp_code if last_otp else None,
                        "is_fresh_otp": True,
                    }
                    return render(request, "app/account/signup.html", context)
                except:
                    return redirect("register")

        if not user_email:
            logger.warning("Resend OTP: Email address is required")
            messages.error(request, "❌ Email address is required.")
            return redirect("register")

        if not get_user_model().objects.filter(email=user_email).exists():
            logger.warning(f"Resend OTP: Email does not exist: {user_email}")
            messages.error(request, "❌ This email doesn't exist in our system.")
            return redirect("register")
        
        user = get_user_model().objects.get(email=user_email)
        logger.info(f"Found user for resend OTP: {user.username}")
        
        last_otp = OtpToken.objects.filter(user=user).order_by('-tp_created_at').first()
        
        # Check cooldown from OTP CREATION time
        if last_otp:
            time_since_creation = timezone.now() - last_otp.tp_created_at
            seconds_remaining = int(60 - time_since_creation.total_seconds())
            
            logger.info(f"OTP age for {user.username}: {time_since_creation.total_seconds()}s, cooldown remaining: {seconds_remaining}s")
            
            if time_since_creation.total_seconds() < 60:
                logger.info(f"Resend OTP cooldown active - cannot resend yet")
                messages.warning(request, f"⏱ Please wait {seconds_remaining} seconds before requesting a new OTP")
                # Return with the EXISTING OTP code, don't create a new one
                form = RegisterForm(instance=user)
                context = {
                    "form": form,
                    "otp_code": last_otp.otp_code,
                    "is_fresh_otp": False,  # Not a fresh OTP, user is just resending
                }
                return render(request, "app/account/signup.html", context)
        
        # Only create new OTP if cooldown has passed
        if last_otp:
            logger.info(f"Cooldown passed, deleting old OTP for user: {user.username}")
            last_otp.delete()
        
        # Clear the fresh OTP flag since we're explicitly resending
        request.session.pop('fresh_otp_timestamp', None)
        request.session.pop('fresh_otp_user', None)
        
        # Create new OTP
        logger.info(f"Creating new OTP for user: {user.username}")
        otp = OtpToken.objects.create(
            user=user, 
            otp_expires_at=timezone.now() + timezone.timedelta(minutes=5),
            last_resend_at=timezone.now()
        )
        logger.info(f"New OTP created: {otp.otp_code}")

        subject = "Email Verification Code - Koya Nardz Shop"
        message = f"""
Dear {user.username},

Your OTP verification code is:
{otp.otp_code}

This code expires in 5 minutes.

If you didn't request this, please ignore this email.

Best regards,
Koya Nardz Shop Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"OTP email sent successfully to {user.email}")
            messages.success(request, "✉ New code sent! Check your email.")
        except Exception as e:
            logger.exception(f"Failed to send OTP email to {user.email}: {str(e)}")
            messages.error(request, "❌ Failed to send email. Please try again.")
        
        # After resending, go back to the OTP verification view with the new code
        form = RegisterForm(instance=user)
        context = {
            "form": form,
            "otp_code": otp.otp_code,
        }
        logger.info(f"Rendering signup.html with new OTP for user: {user.username}")
        return render(request, "app/account/signup.html", context)

    logger.debug("Resend OTP GET request received")
    context = {}
    return render(request, "app/account/resend_otp.html", context)

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST['username_or_email']
        password = request.POST['password']

        user = None
        if '@' in login_input:
            user = get_user_model().objects.filter(email=login_input).first()
        else: 
            user = get_user_model().objects.filter(username=login_input).first()


        if user:
            if user.check_password(password):
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password")
        return redirect("login")

    return render(request, 'app/account/login.html')

def forgot_password(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = get_user_model().objects.filter(email=email)
            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = user.pk
                    # Use Render domain in production, localhost in development
                    if request.is_secure():
                        current_site = get_current_site(request)
                        domain = current_site.domain
                    else:
                        domain = request.get_host()
                    
                    protocol = 'https' if request.is_secure() else 'http'
                    reset_url = f"{protocol}://{domain}/reset-password/{uid}/{token}/"
                    
                    # Send HTML email with professional template
                    subject = "Password Reset Request - Koya Nardz"
                    html_message = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; background-color: #f5f7fa; padding: 20px;">
                            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h2 style="color: #003d99; margin-bottom: 20px;">Password Reset Request</h2>
                                
                                <p style="color: #333; font-size: 16px; line-height: 1.6;">
                                    Hello {user.first_name or user.username},
                                </p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6;">
                                    We received a request to reset the password for your Koya Nardz account. If you did not make this request, you can ignore this email.
                                </p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 20px;">
                                    To reset your password, click the button below. This link will expire in 24 hours.
                                </p>
                                
                                <div style="text-align: center; margin: 30px 0;">
                                    <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto; border-collapse: collapse;">
                                        <tr>
                                            <td style="border-radius: 4px; background-color: #003d99; padding: 0;">
                                                <a href="{reset_url}" style="display: block; background-color: #003d99; color: white; padding: 14px 40px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 16px; border: 2px solid #003d99; mso-padding-alt: 14px 40px;">Reset Password</a>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <p style="color: #999; font-size: 12px; line-height: 1.6; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                                    If the button above doesn't work, click this link:<br/>
                                    <a href="{reset_url}" style="color: #0b84c6; text-decoration: underline; word-break: break-all;">{reset_url}</a>
                                </p>
                                
                                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                                    Best regards,<br/>
                                    Koya Nardz Team
                                </p>
                            </div>
                        </body>
                    </html>
                    """
                    
                    send_mail(
                        subject,
                        f"Click the link to reset your password: {reset_url}",
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                messages.success(request, "Password reset link has been sent to your email. Please check your inbox and spam folder.")
                return redirect('login')
            else:
                messages.warning(request, "No account with this email exists.")
                return redirect('forgot_password')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'app/account/forgotpassword.html', {'form': form})

def reset_password(request, uid, token):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=uid)
    except UserModel.DoesNotExist:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "Your password has been reset successfully! You are now logged in.")
                return redirect('home')
        else:
            form = CustomSetPasswordForm(user)
    else:
        messages.error(request, "The reset link is invalid or has expired. Please request a new password reset.")
        return redirect('forgot_password')

    return render(request, 'app/account/password_reset.html', {'form': form})

@login_required
def user_profile(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    # Handle avatar-only update
    if request.method == 'POST' and 'avatar' in request.FILES and 'save_profile' not in request.POST and 'change_password' not in request.POST:
        from app.forms import AvatarForm
        avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if avatar_form.is_valid():
            user = avatar_form.save()
            
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully!',
                    'avatar_url': user.avatar.url if user.avatar else '',
                })
            else:
                messages.success(request, 'Profile picture updated successfully!')
                return redirect('profile')
        else:
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error updating profile picture',
                    'errors': avatar_form.errors
                })
            else:
                messages.error(request, 'Error updating profile picture. Please check the image.')

    elif request.method == 'POST' and 'save_profile' in request.POST:
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            user = profile_form.save()
            
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully!',
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'contact': user.contact,
                    'address': user.address,
                })
            else:
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        else:
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error updating profile',
                    'errors': profile_form.errors
                })
            else:
                messages.error(request, 'Error updating profile. Please check your inputs.')
                
    elif request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Password updated successfully!'
                })
            else:
                messages.success(request, 'Password updated successfully!')
                return redirect('profile')
        else:
            # Check if this is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error updating password',
                    'errors': password_form.errors
                })
            else:
                messages.error(request, 'Error updating password. Please check your inputs.')

    return render(request, 'app/account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

def logout_view(request):
    logout(request)
    # Clear any remaining messages from session
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    storage.used = True
    return redirect('home') 

#END REGISTER & LOGIN
@csrf_exempt
@require_POST
def add_pc_build_to_cart(request):
    try:
        data = json.loads(request.body)
        parts = data.get('parts', [])

        cart = request.session.get('cart', {})

        for part in parts:
            product_id = str(part['id'])
            quantity = part.get('quantity', 1)

            produkto = Product.objects.get(pk=product_id)

            if product_id in cart:
                cart[product_id]['quantity'] += quantity
                if cart[product_id]['quantity'] > produkto.stock:
                    cart[product_id]['quantity'] = produkto.stock
            else:
                cart[product_id] = {
                    'image': produkto.image.url if produkto.image else None,
                    'product_name': produkto.product_name,
                    'price': float(produkto.price),
                    'quantity': min(quantity, produkto.stock),
                }

        request.session['cart'] = cart

        return JsonResponse({
            'message': 'PC Build added to cart!',
            'cart_count': sum(item['quantity'] for item in cart.values())
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            variant_id = data.get("variant_id")
        else: 
            quantity = int(request.POST.get('quantity', 1))
            variant_id = request.POST.get("variant_id")

        cart = request.session.get('cart', {})
        if variant_id:
            variant = get_object_or_404(ProductVariation, pk=variant_id)
            cart_key = f"variant-{variant_id}"

            if cart_key in cart:
                cart[cart_key]["quantity"] += quantity
                if cart[cart_key]["quantity"] > variant.stock:
                    cart[cart_key]["quantity"] = variant.stock
            else:
                cart[cart_key] = {
                    "image": variant.image.url if variant.image else None,
                    "product_name": f"{variant.product.product_name} ({variant.product_variation})",
                    "price": float(variant.price),
                    "quantity": min(quantity, variant.stock),
                    "variant_id": variant_id,
                    "product_id": product_id,
                }
        else:
            produkto = get_object_or_404(Product, pk=product_id)

            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity
                if cart[str(product_id)]['quantity'] > produkto.stock:
                    cart[str(product_id)]['quantity'] = produkto.stock
            else:
                cart[str(product_id)] = {
                    'image': produkto.image.url if produkto.image else None,
                    'product_name': produkto.product_name,
                    'price': float(produkto.price),
                    'quantity': min(quantity, produkto.stock),
                    "product_id": product_id,
                }

        request.session['cart'] = cart

        if request.content_type == 'application/json':
            return JsonResponse({'message': 'Product added successfully!', 'cart_count': sum(item['quantity'] for item in cart.values())})
        return redirect('cart')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        # Prefer an explicit cart_key sent by the form (this will be the
        # session dict key, e.g. 'variant-6' or '6'). Fall back to using
        # the numeric product_id from the URL.
        posted_cart_key = request.POST.get('cart_key')

        if posted_cart_key:
            # Use posted key directly
            cart_key = str(posted_cart_key)
            if cart_key in cart:
                item = cart[cart_key]
                # Determine stock depending on whether this is a variant
                if cart_key.startswith('variant-'):
                    variant = get_object_or_404(ProductVariation, pk=item.get('variant_id'))
                    stock = variant.stock
                else:
                    stock = get_object_or_404(Product, pk=item.get('product_id')).stock
            else:
                return redirect(request.META.get('HTTP_REFERER', 'cart'))
        else:
            cart_key = str(product_id)
            variant_key = f"variant-{product_id}"

            if cart_key in cart:
                item = cart[cart_key]
                stock = get_object_or_404(Product, pk=product_id).stock
            elif variant_key in cart:
                item = cart[variant_key]
                variant = get_object_or_404(ProductVariation, pk=item["variant_id"])
                stock = variant.stock
                cart_key = variant_key
            else:
                return redirect(request.META.get('HTTP_REFERER', 'cart'))

        action = request.POST.get('action')
        current_quantity = item['quantity']

        if action == 'increase':
            if current_quantity < stock:
                item['quantity'] += 1
        elif action == 'decrease':
            if current_quantity > 1:
                item['quantity'] -= 1
        else:
            quantity = int(request.POST.get('quantity', 1))
            item['quantity'] = max(1, min(quantity, stock))
        
        cart[cart_key] = item
        request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        # Allow an explicit cart_key to be sent (handles keys like 'variant-6')
        posted_cart_key = request.POST.get('cart_key')
        if posted_cart_key:
            key = str(posted_cart_key)
            if key in cart:
                del cart[key]
        else:
            cart_key = str(product_id)
            variant_key = f"variant-{product_id}"

            if cart_key in cart:
                del cart[cart_key]
            elif variant_key in cart:
                del cart[variant_key]

        request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def get_cart_data(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'cart_products': list(cart.values())})

def direct_checkout(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        # Optional variant id may be provided (from product item Buy Now)
        variant_id = request.POST.get('variant_id')

        dc = {
            'product_id': product_id,
            'quantity': quantity
        }
        if variant_id:
            dc['variant_id'] = variant_id
        request.session['direct_checkout'] = dc
        return redirect('appointment')
    return redirect('product')

@require_POST
def update_direct_checkout(request):
    """Update quantity for direct checkout item on checkout page."""
    action = request.POST.get('action')
    direct = request.session.get('direct_checkout', {})

    if direct and action:
        # Get product/variant to check stock
        variant_id = direct.get('variant_id')
        product_id = direct.get('product_id')

        if variant_id:
            variant = get_object_or_404(ProductVariation, pk=variant_id)
            stock = variant.stock
        else:
            product = get_object_or_404(Product, pk=product_id)
            stock = product.stock

        current_qty = direct.get('quantity', 1)

        if action == 'increase':
            if current_qty < stock:
                direct['quantity'] = current_qty + 1
        elif action == 'decrease':
            if current_qty > 1:
                direct['quantity'] = current_qty - 1

        request.session['direct_checkout'] = direct

    return redirect(request.META.get('HTTP_REFERER', 'checkout'))

@csrf_protect
@require_POST
def toggle_favorite(request, product_id):
    """Toggle favorite - uses DB for authenticated users, session for anonymous"""
    try:
        # Verify product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
        
        removed = False
        
        # Handle authenticated users with database
        if request.user.is_authenticated:
            fav = Favorite.objects.filter(user=request.user, favorite_product=product).first()
            if fav:
                fav.delete()
                removed = True
            else:
                Favorite.objects.create(user=request.user, favorite_product=product)
            
            # Get all user's favorites from database
            favorites = Favorite.objects.filter(user=request.user).values_list('favorite_product_id', flat=True)
            favorite_ids = list(favorites)
        else:
            # Handle anonymous users with session
            session_favs = request.session.get('favorites', [])
            prod_id_str = str(product_id)
            
            if prod_id_str in session_favs:
                session_favs.remove(prod_id_str)
                removed = True
            else:
                session_favs.append(prod_id_str)
            
            request.session['favorites'] = session_favs
            request.session.modified = True
            
            # Convert session favorites to integers
            favorite_ids = []
            for fav_id in session_favs:
                try:
                    favorite_ids.append(int(fav_id))
                except (ValueError, TypeError):
                    pass
        
        # Build response
        response_data = {
            "status": "removed" if removed else "added",
            "product": {
                "id": product.id,
                "name": product.product_name,
                "img": product.image.url if product.image else ""
            }
        }
        
        # Generate dropdown HTML with all favorited products
        favorite_products = Product.objects.filter(id__in=favorite_ids) if favorite_ids else []
        
        dropdown_html = ""
        if favorite_products:
            for fav in favorite_products:
                img_url = fav.image.url if fav.image else ""
                dropdown_html += f'<div class="fav-item" data-product-id="{fav.id}"><div class="fav-left"><a href="/product_item/{fav.id}/"><img src="{img_url}" alt="{fav.product_name}" style="width:40px;height:40px;object-fit:cover;"></a><div class="fav-meta">{fav.product_name}</div></div><div class="fav-actions"><button type="button" class="fav-remove-btn" data-product-id="{fav.id}" aria-label="Remove"><i class="fa-solid fa-trash-alt"></i></button></div></div>'
        else:
            dropdown_html = '<p class="no-fav">No favorites yet</p>'
        
        response_data['dropdown_html'] = dropdown_html
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)




@csrf_exempt
def submit_rating_ajax(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=403)

    produkto = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get("rating", 0))

    review, created = ProductReview.objects.get_or_create(
        product=produkto, user=request.user
    )
    review.rating = rating
    review.save()

    reviews = produkto.reviews.all()
    avg = round(sum(r.rating for r in reviews) / reviews.count(), 1)

    return JsonResponse({
        "success": True,
        "rating": review.rating,
        "average": avg,
        "count": reviews.count(),
    })


@csrf_exempt
def submit_comment_ajax(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=403)

    produkto = get_object_or_404(Product, id=product_id)
    comment = request.POST.get("comment", "")

    review, created = ProductReview.objects.get_or_create(
        product=produkto,
        user=request.user
    )
    review.comment = comment
    review.save()

    return JsonResponse({
        "success": True,
        "comment": review.comment,
        "rating": review.rating,
        "created": review.created_at.strftime("%b %d, %Y"),
        "username": request.user.username
    })


@login_required
def appoint(request):
    form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            count = Appointment.objects.filter(date=selected_date).count()

            if count >= 10:
                form.add_error('date', 'Maximum appointments reached for this date.')
            else:
                request.session['appointment_data'] = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'contact': form.cleaned_data['contact'],
                    'email': form.cleaned_data['email'],
                    'date': selected_date.isoformat(),
                    'time': form.cleaned_data['time']
                }
                return redirect('checkout') 
    
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = AppointmentForm(initial=initial_data)

    appointments = Appointment.objects.all()
    events = [{
            'title': f"{appoint.first_name} {appoint.last_name}",  
            'start': appoint.date.strftime('%Y-%m-%d'),
            'color': 'green'
        }for appoint in appointments]

    # Get product information from direct_checkout session if available
    direct_checkout = request.session.get('direct_checkout')
    product_info = None
    if direct_checkout:
        try:
            product = Product.objects.get(id=direct_checkout.get('product_id'))
            product_info = {
                'product_id': product.id,
                'product_name': product.product_name,
                'price': product.price,
                'quantity': direct_checkout.get('quantity', 1),
                'image': product.image.url if product.image else None,
                'total_price': product.price * direct_checkout.get('quantity', 1)
            }
        except Product.DoesNotExist:
            product_info = None

    return render(request, 'app/buying/appointment.html', {
        'form': form,
        'events': json.dumps(events),
        'product_info': product_info,
        'direct_checkout': direct_checkout
    })

def appointing(request):
    appointments = Appointment.objects.all()
    events = [{
        'product_name': f"{a.first_name} {a.last_name}",
        'start': f"{a.date}T{a.time}",
    } for a in appointments]
    return JsonResponse(events, safe=False)

def get_available_times(request):
    selected_date = request.GET.get('date')
    
    all_slots = [
        "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00"
    ]

    booked = Appointment.objects.filter(date=selected_date).values_list('time', flat=True)
    booked_times = [t.strftime("%H:%M") for t in booked]
    free_slots = [t for t in all_slots if t not in booked_times]

    return JsonResponse({'available_times': free_slots})

def get_booked_dates(request):
    appointments = Appointment.objects.values('date').annotate(count=models.Count('id'))

    fully_booked = [
        a['date'].strftime('%Y-%m-%d')
        for a in appointments
        if a['count'] >= 10
    ]

    return JsonResponse({'blocked_dates': fully_booked})

def get_appointment_counts(user):
    if not user.is_authenticated:
        return {
            'count_all': 0,
            'count_pending': 0,
            'count_completed': 0,
            'count_cancelled': 0
        }

    today = timezone.now().date()
    
    view_apps = Appointment.objects.filter(email=user.email)
    sell_apps = Selling.objects.filter(email=user.email)

    return {
        'count_all': view_apps.count() + sell_apps.count(),
        'count_pending': view_apps.filter(status="Pending", date__gte=today).count() +
                         sell_apps.filter(status="Pending", selling_date__gte=today).count(),
        'count_completed': view_apps.filter(status__in=["Completed", "Finished"]).count() +
                           sell_apps.filter(status="Completed").count(),
        'count_cancelled': view_apps.filter(status="Cancelled").count() +
                           sell_apps.filter(status="Cancelled").count(),
    }


@require_POST
def finished_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Finished'
    appointment.save()
    messages.success(request, "Marked as Finished")
    return redirect('admin_appointment')

@require_http_methods(["GET", "POST"])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "")
        appointment.status = "Cancelled"
        appointment.cancel_reason = reason
        appointment.save()

        try:
            send_mail(
                subject='Your Appointment Has Been Cancelled',
                message=f"Hello {appointment.first_name},\n\nYour appointment (Ref: {appointment.reference_number}) has been cancelled.\n\nReason: {reason}\n\nThank you.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[appointment.email],
                fail_silently=False,
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to send cancellation email for appointment {appointment.id}")

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@require_http_methods(["GET", "POST"])
def cancel_trade(request, selling_id):
    selling = get_object_or_404(Selling, id=selling_id)

    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "")
        selling.status = "Cancelled"
        selling.cancel_reason = reason
        selling.save()

        try:
            send_mail(
                subject='Your Trade Has Been Cancelled',
                message=f"Hello {selling.first_name},\n\nYour appointment for trade (Ref: {selling.reference_number}) has been cancelled.\n\nReason: {reason}\n\nThank you.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[selling.email],
                fail_silently=False,
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to send trade cancellation email for selling {selling.id}")

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@require_POST
def complete_trade(request, selling_id):
    trade = get_object_or_404(Selling, id=selling_id)
    trade.status = 'Completed'
    trade.save()
    return redirect('admin_selling')

@login_required
def my_appointment_history(request):
    appointments = Appointment.objects.filter(email=request.user.email).order_by('-date')
    return render(request, 'app/admin/my_historyappointment.html', {'appointments': appointments})

class HomePage(TemplateView):
    template_name = 'app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Only get products with valid image files
        products = Product.objects.exclude(image='').exclude(image__isnull=True).order_by('-created_at')[:5]
        # Filter to only include products where the image file actually exists
        valid_products = []
        for p in products:
            try:
                # Try to access the image URL to ensure file exists
                if p.image and p.image.url:
                    valid_products.append(p)
            except (ValueError, AttributeError):
                # Skip products where image file doesn't exist
                pass
        context['products'] = valid_products
        return context

class ProductPage(TemplateView):
    model = Product
    template_name = 'app/buying/product.html'
    context_object_name = 'products'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    COMPONENT_TO_GBL = {
    "cpu": "cpu.gbl",
    "motherboard": "motherboard.gbl",
    "ram": "ram.gbl",
    "gpu": "gpu.gbl",
    "psu": "psu.gbl",
    "case": "case.gbl",
    "cooling": "cooling.gbl",
    "monitor": "monitor.gbl",
    "storage": "storage.gbl",
}
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
    
        search_query = self.request.GET.get('search', '').strip()
        category_filter = self.request.GET.get('category', '').strip()
        brand_filter = self.request.GET.get('brand', '').strip()
        price_order = self.request.GET.get('price_order', '').strip()

        products = Product.objects.all()

        if search_query:
            products = products.filter(
                Q(category_name__category_name__icontains=search_query) |
                Q(brand__brand__icontains=search_query) |
                Q(product_name__icontains=search_query) 
            )

        # Convert category_filter to integer if it exists
        if category_filter:
            try:
                category_id = int(category_filter)
                products = products.filter(category_name__id=category_id)
                brands = Brand.objects.filter(product__category_name__id=category_id).distinct().order_by('brand')
            except (ValueError, TypeError):
                brands = Brand.objects.annotate(product_count=Count('product')).order_by('brand')
        else:
            brands = Brand.objects.annotate(product_count=Count('product')).order_by('brand')
        
        # Sort brands alphabetically with "Others" at the end
        brands_list = list(brands)
        others_brand = None
        regular_brands = []
        for brand in brands_list:
            if brand.brand.lower() == 'others':
                others_brand = brand
            else:
                regular_brands.append(brand)
        
        if others_brand:
            brands = regular_brands + [others_brand]
        else:
            brands = regular_brands
        
        # Convert brand_filter to integer if it exists
        if brand_filter:
            try:
                brand_id = int(brand_filter)
                products = products.filter(brand__id=brand_id)
            except (ValueError, TypeError):
                pass

        # Always annotate total_bought for all products to show best seller tag
        products = products.annotate(
            total_bought=Sum('appointmentproduct__quantity')
        )

        if price_order == 'high':
            products = products.order_by('-price')
        elif price_order == 'low':
            products = products.order_by('price')
        elif price_order == 'newest':
            products = products.order_by('-created_at')
        elif price_order == 'oldest':
            products = products.order_by('created_at')
        elif price_order == 'most_buy':
            products = products.order_by('-total_bought')
        else:
            products = products.order_by('-created_at')
        
        # Filter to only include products with valid images
        valid_products = filter_products_with_valid_images(products)
        
        context.update({
            'products': valid_products,
            'brands': brands,
            'search_query': search_query,
            'category_filter': category_filter,
            'brand_filter': brand_filter,
        })
        context['price_order'] = price_order
        # Add Gemini API key to context
        context['gemini_api_key'] = os.getenv('GEMINI_API_KEY', '')
        return context

class ProductItemPage(TemplateView):
    template_name = 'app/buying/product_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        produkto = get_object_or_404(Product, id=product_id)
        variant_id = self.request.GET.get("variant")

        if variant_id:
            try:
                selected_variant = produkto.variations.get(id=variant_id)
                context["selected_variant"] = selected_variant
                context["price"] = selected_variant.price
                context["stock"] = selected_variant.stock
                # Use variant image(s) when a variant is selected
                images = []
                if selected_variant.image:
                    images = [selected_variant.image.url]
                context["images"] = images
            except ProductVariation.DoesNotExist:
                context["selected_variant"] = None
                context["price"] = produkto.price
                context["stock"] = produkto.stock
                context["images"] = produkto.images.all()
        else:
            context["selected_variant"] = None
            context["price"] = produkto.price
            context["stock"] = produkto.stock
            context["images"] = [img.product_image.url for img in produkto.images.all()]
        
        # Filter to only include products with valid images
        related_products = Product.objects.exclude(id=produkto.id).order_by('-created_at')[:30]
        context["products"] = filter_products_with_valid_images(related_products)

        reviews = produkto.reviews.all().order_by("-created_at")
        context["reviews"] = reviews

        if reviews.exists():
            context["average_rating"] = round(sum(r.rating for r in reviews) / reviews.count(), 1)
        else:
            context["average_rating"] = 0
        
        # Get user's existing review if authenticated
        if self.request.user.is_authenticated:
            try:
                user_review = reviews.get(user=self.request.user)
                context["user_review"] = user_review
            except:
                context["user_review"] = None
        
        context["review_form"] = ProductReviewForm()
        context["produkto"] = produkto
        # build display fields for template: name, description, main image and thumbnails
        if context.get("selected_variant"):
            sv = context["selected_variant"]
            # display name: base name + variant label
            context["display_name"] = f"{produkto.product_name} — {sv.product_variation}"
            # prefer variant description if provided
            context["display_description"] = sv.description if sv.description else (produkto.description or "")
            # main image and thumbnails are already in context['images'] (list of URLs)
            thumbnails = context.get("images", [])
        else:
            context["display_name"] = produkto.product_name
            context["display_description"] = produkto.description or ""
            thumbnails = context.get("images", [])

        # Ensure thumbnails is a list of URLs (already handled above), and set main_image
        context["thumbnails"] = thumbnails
        context["main_image"] = thumbnails[0] if thumbnails else (produkto.image.url if produkto.image else "")
        context["variations"] = produkto.variations.all()
        return context
    
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id")
        produkto = get_object_or_404(Product, id=product_id)

        form = ProductReviewForm(request.POST)
        if form.is_valid():
            # Check if user already has a review for this product
            try:
                existing_review = produkto.reviews.get(user=request.user)
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
            except produkto.reviews.model.DoesNotExist:
                # Create new review if none exists
                review = form.save(commit=False)
                review.product = produkto
                review.user = request.user
                review.save()

        return redirect("product_item", product_id=product_id)

class AppointmentPage(TemplateView):
    template_name = 'app/buying/appointment.html'

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        today = date.today()

        if selected_date < today:
            raise ValidationError("You cannot select a past date for an appointment.")
        
        return selected_date

class AIBotPage(TemplateView):
    template_name = 'app/buying/aibot.html'

class CheckoutPage(TemplateView):
    template_name = 'app/buying/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_data = self.request.session.get('appointment_data')

        if appointment_data.get('time'):
            time_obj = datetime.strptime(appointment_data['time'], "%H:%M")
            appointment_data['time'] = time_obj.strftime("%I:%M %p")

        context['appointment_datas'] = appointment_data

        direct = self.request.session.get('direct_checkout')

        if direct:
            product = get_object_or_404(Product, pk=direct['product_id'])
            quantity = int(direct.get('quantity', 1))

            checkout_item = {
                'product_name': product.product_name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else None,
                'product_id': product.id,
                'sub_total': float(product.price) * quantity
            }
            context['cart_products'] = [checkout_item]     
            context['total_price'] = checkout_item['sub_total']
            context['is_direct'] = True
            return context
        
        cart = self.request.session.get('cart', {})
            
        for product_id, produkto in cart.items():
            produkto['sub_total'] = float(produkto['price']) * int(produkto['quantity'])
            # Preserve numeric product_id stored when item was added to cart
            # (don't overwrite it with the session key which may be 'variant-6')
            if 'product_id' not in produkto:
                produkto['product_id'] = product_id
            produkto['cart_key'] = product_id

        context['cart_products'] = cart.values()
        context['total_price'] = sum(item['sub_total'] for item in cart.values())
        context['is_direct'] = False
        return context

class AppointmentCompletePage(TemplateView):
    template_name = 'app/buying/appointment_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        all_products = Product.objects.all().order_by('-created_at')[:30]
        context['products'] = filter_products_with_valid_images(all_products)
        return context

    def get(self, request, *args, **kwargs):
        complete_data = request.session.get('appointment_complete')
        if not complete_data:
            return redirect('appointment')
        context = self.get_context_data()
        context['reference_number'] = complete_data.get('reference_number')
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        appointment_data = request.session.get('appointment_data')
        cart = request.session.get('cart', {})
        direct = request.session.get('direct_checkout')

        # Ensure we have appointment data (date/time). If it's missing
        # we cannot create an appointment — redirect back to the appointment
        # page. This also avoids accessing `appointment_data[...]` when
        # `appointment_data` is None (which caused a 500 for some flows).
        if not appointment_data:
            return redirect('appointment')

        if Appointment.objects.filter(
            date=appointment_data['date'], 
            time=appointment_data['time']).exists():
            return redirect('checkout')

        appointment = Appointment.objects.create(
            first_name=appointment_data['first_name'],
            last_name=appointment_data['last_name'],
            contact=appointment_data['contact'],
            email=appointment_data['email'],
            date=date.fromisoformat(appointment_data['date']),
            time=time.fromisoformat(appointment_data['time']), 
        )

        product_list = [] 
        total_price = 0
        
        if direct:
            # Support variant-aware direct checkout. If a variant_id was stored
            # use the variant's price and decrement variant stock; otherwise
            # use the base product price and decrement product stock.
            variant_id = direct.get('variant_id')
            if variant_id:
                variant = get_object_or_404(ProductVariation, pk=variant_id)
                product = variant.product
                price_used = float(variant.price)
            else:
                product = Product.objects.get(id=direct['product_id'])
                variant = None
                price_used = float(product.price)

            quantity = int(direct['quantity'])
            subtotal = price_used * quantity
            total_price += subtotal

            AppointmentProduct.objects.create(
                appointment=appointment,
                product=product,
                quantity=quantity,
                price=price_used,
                variation=(variant.product_variation if variant else None),
            )

            # Decrement stock safely (don't let it go negative)
            if variant:
                variant.stock = max(0, variant.stock - quantity)
                variant.save()
            else:
                product.stock = max(0, product.stock - quantity)
                product.save()

            name = product.product_name
            if variant:
                name = f"{name} ({variant.product_variation})"

            product_list.append({
                "name": name,
                "quantity": quantity,
                "price": price_used,
                "subtotal": subtotal,
            })

            del request.session['direct_checkout']
        

        else:
            for cart_key, produkto in cart.items():
                # cart_key may be a numeric product id string (e.g. '22')
                # or a variant key like 'variant-6'. Resolve the actual
                # Product instance accordingly.
                if str(cart_key).startswith('variant-'):
                    variant_id = produkto.get('variant_id')
                    if variant_id:
                        variant = get_object_or_404(ProductVariation, pk=variant_id)
                        product = variant.product
                    else:
                        # fallback: try to use stored product_id inside the item
                        pid = produkto.get('product_id')
                        product = get_object_or_404(Product, pk=pid)
                else:
                    # numeric key
                    product = get_object_or_404(Product, pk=int(cart_key))

                quantity = int(produkto.get('quantity', 1))
                price = float(produkto.get('price', product.price))
                subtotal = quantity * price
                total_price += subtotal

                # If this cart entry was for a variant, record the variation
                # name on the AppointmentProduct and include it in emails.
                variation_name = None
                if str(cart_key).startswith('variant-'):
                    variation_name = produkto.get('product_name')
                    # `product_name` for variant entries is like "Base Name (Variation)"; try
                    # to extract the parenthetical variation if present.
                    if variation_name and '(' in variation_name and variation_name.endswith(')'):
                        # extract text inside final parentheses
                        variation_name = variation_name.split('(')[-1].rstrip(')')

                AppointmentProduct.objects.create(
                    appointment=appointment,
                    product=product,
                    quantity=quantity,
                    price=price,
                    variation=variation_name,
                )

                # Decrement stock safely for variant or base product
                try:
                    if str(cart_key).startswith('variant-') and 'variant' in locals() and variant:
                        variant.stock = max(0, variant.stock - quantity)
                        variant.save()
                    else:
                        product.stock = max(0, product.stock - quantity)
                        product.save()
                except Exception:
                    # If stock decrement fails for any reason, log and continue
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.exception(f"Failed to decrement stock for product in appointment {appointment.id}")

                display_name = product.product_name
                if variation_name:
                    display_name = f"{display_name} ({variation_name})"

                product_list.append({
                    "name": display_name,
                    "quantity": quantity,
                    "price": price,
                    "subtotal": subtotal,
                })

            if "cart" in request.session:
                del request.session['cart']

        email_html = render_to_string( 
            'app/buying/appointment_confirmation.html', 
            { 
                "first_name": appointment.first_name, 
                "reference_number": appointment.reference_number, 
                "date": appointment.date, 
                "time": appointment.time, 
                "products": product_list, 
                "total_price": total_price, 
            }
        ) 
            
        # Send confirmation email, but don't let email failures produce a 500
        try:
            send_email(
                subject=f"Appointment Confirmation – Ref #{appointment.reference_number}",
                text="",
                html=email_html,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                recipient_list=[appointment.email],
            )
        except Exception:
            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to send appointment confirmation email for appointment {appointment.id}")
            
        del request.session['appointment_data']

        request.session['appointment_complete'] = {
            'reference_number': appointment.reference_number
        }

        return redirect('appointment_complete')

class SellingPage(TemplateView):
    template_name = 'app/selling/selling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SellingForm()
        
        # Pre-fill form with authenticated user's data
        if self.request.user.is_authenticated:
            form.initial = {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'contact': self.request.user.phone_number if hasattr(self.request.user, 'phone_number') else '',
                'address': self.request.user.address if hasattr(self.request.user, 'address') else '',
            }
        
        context['form'] = form
        return context
    
    def post(self, request, *args, **kwargs):
        form = SellingForm(request.POST, request.FILES)
        if form.is_valid():
            selling_appointment = form.save(commit=False)
            
            # Ensure email matches authenticated user's email for proper tracking
            if request.user.is_authenticated:
                selling_appointment.email = request.user.email
            
            selling_appointment.save()

            selling_appointment.reference_number = selling_appointment.reference_number
            selling_appointment.save()

            messages.success(request, 'Selling appointment submitted successfully!')
            request.session['reference_number'] = selling_appointment.reference_number
            request.session['selling_id'] = selling_appointment.id
            return redirect('selling_complete')

        return self.render_to_response({'form': form})

class SellingCompletePage(TemplateView):
    template_name = 'app/selling/selling_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reference_number'] = self.request.session.get('reference_number')
        
        # Retrieve the selling appointment details
        selling_id = self.request.session.get('selling_id')
        if selling_id:
            try:
                selling = Selling.objects.get(id=selling_id)
                context['selling'] = selling
                context['selling_data'] = {
                    'first_name': selling.first_name,
                    'last_name': selling.last_name,
                    'contact': selling.contact,
                    'email': selling.email,
                    'address': selling.address,
                    'selling_date': selling.selling_date,
                    'selling_time': selling.selling_time,
                    'product_name': selling.product_name,
                    'category': selling.category.category_name if selling.category else 'N/A',
                    'price': selling.price,
                    'description': selling.description,
                    'image': selling.image.url if selling.image else None,
                }
            except Selling.DoesNotExist:
                context['selling'] = None
                context['selling_data'] = None
        else:
            context['selling'] = None
            context['selling_data'] = None
        
        return context

class SellingInfoPage(TemplateView):
    template_name = 'app/selling/selling_information.html'


class MyAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        if user.is_authenticated:
            today = timezone.now().date()
            appointments = Appointment.objects.filter(email=user.email) \
                .exclude(status__in=['Cancelled', 'Finished']) \
                .filter(date__gte=today) \
                .order_by('-created_at')

            if status_filter:
                appointments = appointments.filter(status=status_filter)

            if search_query:
                appointments = appointments.filter(
                    Q(reference_number__icontains=search_query)
                )

            context['appointments'] = appointments
        else:
            context['appointments'] = []

        return context


class MySellingAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_sellingappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        if user.is_authenticated:
            # Show all selling appointments regardless of date
            sellings = Selling.objects.filter(email=user.email) \
                .exclude(status__in=['Cancelled']) \
                .order_by('-selling_date')

            if status_filter:
                sellings = sellings.filter(status=status_filter)

            if search_query:
                sellings = sellings.filter(
                    Q(reference_number__icontains=search_query)
                )

            context['sellings'] = sellings
        else:
            context['sellings'] = []

        return context

class MyCancelledAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_cancelledappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        counts = get_appointment_counts(user)
        context.update(counts)

        if user.is_authenticated:
            c1 = Appointment.objects.filter(email=user.email, status="Cancelled")
            c2 = Selling.objects.filter(email=user.email, status="Cancelled")

            appointments = sorted(
                list(c1) + list(c2),
                key=lambda x: getattr(x, "created_at", getattr(x, "selling_at", None)),
                reverse=True
            )

            context['appointments'] = appointments
            context['count_viewing'] = c1.count()
            context['count_selling'] = c2.count()
        else:
            context['appointments'] = []
            context['count_viewing'] = 0
            context['count_selling'] = 0

        return context

class MyHistoryAppointmentPage(TemplateView):
    template_name = 'app/appointment/my_historyappointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('q', '')

        counts = get_appointment_counts(user)
        context.update(counts)

        if user.is_authenticated:
            history_appointments = Appointment.objects.filter(email=user.email, status__in=['Cancelled', 'Finished']).order_by('-created_at')
            history_sellings = Selling.objects.filter(email=user.email, status__in=['Cancelled', 'Completed']).order_by('-selling_at')
            
            historyappointment = list(history_appointments) + list(history_sellings)
            historyappointment = sorted(historyappointment, key=lambda x: getattr(x, 'created_at', getattr(x, 'selling_at', None)), reverse=True)
            
            if status_filter:
                appointments = appointments.filter(status=status_filter)
        
            if search_query:
                appointments = appointments.filter(
                    Q(reference_number__icontains=search_query) |
                    Q(products__product__product_name__icontains=search_query)
                ).distinct()

            if not historyappointment:
                context['no_history_appointments'] = True  
        else:
            historyappointment = []
            context['no_history_appointments'] = True  

        context['historyappointment'] = historyappointment
        context['status_filter'] = status_filter
        context['search_query'] = search_query
        return context

class CartPage(TemplateView):
    template_name = 'app/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})

        # Enhance cart data with product category information
        for product_id, produkto in cart.items():
            produkto['sub_total'] = produkto['price'] * produkto['quantity']
            if 'product_id' not in produkto:
                produkto['product_id'] = product_id
            produkto['cart_key'] = product_id
            
            # Add category information if not already present
            if 'category_name' not in produkto and 'product_id' in produkto:
                try:
                    product = Product.objects.get(id=produkto['product_id'])
                    produkto['category_name'] = product.category_name.category_name if product.category_name else 'Unknown'
                except Product.DoesNotExist:
                    produkto['category_name'] = 'Unknown'

        context['cart_products'] = cart
        context['total_price'] = sum(produkto['price'] * produkto['quantity'] for produkto in cart.values())
        context['favorites'] = self.request.session.get('favorites', [])
        all_products = Product.objects.all().order_by('-created_at')[:30]
        context['products'] = filter_products_with_valid_images(all_products)
        return context

class FavoritePage(TemplateView):
    template_name = 'app/favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorites = self.request.session.get('favorites', [])
        products = Product.objects.filter(id__in=favorites)
        
        # Filter to only include products with valid images
        context['products'] = filter_products_with_valid_images(products)
        return context

#ADMIN
class AdminDashboard(TemplateView):
    template_name = 'app/admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_appointments = Appointment.objects.exclude(status__in=['Cancelled', 'Pending']).count()
        total_trades = Selling.objects.exclude(status__in=['Cancelled', 'Pending']).count()

        today = timezone.now().date()
        appointed = Appointment.objects.filter(status='Pending', created_at__date=today).count()
        traded = Selling.objects.filter(status='Pending', selling_at__date=today).count()

        days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        appointment_chart_labels = []
        appointment_chart_data = []
        selling_chart_labels = []
        selling_chart_data = []

        for day in days:
            appointment_count = Appointment.objects.filter(created_at__date=day).count()
            selling_count = Selling.objects.filter(selling_at__date=day).count()

            appointment_chart_labels.append(day.strftime('%Y-%m-%d'))
            appointment_chart_data.append(appointment_count)

            selling_chart_labels.append(day.strftime('%Y-%m-%d'))
            selling_chart_data.append(selling_count)
        
        categories = Category.objects.all()
        top_categories = []

        for cat in categories:
            sold = AppointmentProduct.objects.filter(product__category_name=cat).aggregate(total=Sum('quantity'))['total'] or 0
            top_categories.append({"category_name": cat.category_name,"total_sold": sold})
            
        total_sales = AppointmentProduct.objects.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        top_categories = sorted(top_categories, key=lambda x: x['total_sold'], reverse=True)
        
        all_orders = []

        for appt in Appointment.objects.filter(status='Pending'):
            delta_days = (timezone.now().date() - appt.date).days
            progress = 100 if delta_days >= 0 else 0

            total_amount = appt.products.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0

            first_product = appt.products.first()
            product_image = first_product.product.image.url if first_product and first_product.product and first_product.product.image else ""
            
            product_list = ", ".join([f"{p.product.product_name if p.product else 'Unknown Product'} x {p.quantity}" for p in appt.products.all()])

            all_orders.append({
                "type": "Appointment",
                "product": ", ".join([f"{p.product.product_name if p.product else 'Unknown Product'} x {p.quantity}" for p in appt.products.all()]),
                "photo": product_image,
                "product_id": appt.reference_number,
                "amount": total_amount,
                "date": appt.created_at,
                "shipping_progress": progress,
                "status": appt.status,
            })
        
        for sell in Selling.objects.filter(status='Pending'):
            delta_days = (timezone.now().date() - sell.selling_date).days
            progress = 100 if delta_days >= 0 else 0

            all_orders.append({
                "type": "Selling",
                "product": sell.product_name,
                "photo": sell.image.url if sell.image else "",
                "product_id": sell.reference_number,
                "amount": sell.price,
                "date": sell.selling_at,
                "shipping_progress": progress,
                "status": sell.status,
            })
        
        all_orders = sorted(all_orders, key=lambda x: x['date'], reverse=True)
        context['all_orders'] = all_orders

        context['category_labels'] = [c['category_name'] for c in top_categories]
        context['category_data'] = [c['total_sold'] for c in top_categories]
        context['category_list'] = top_categories
        context['chart_labels'] = appointment_chart_labels
        context['appointment_chart_data'] = appointment_chart_data
        context['selling_chart_data'] = selling_chart_data
        context['total_appointments'] = total_appointments
        context['total_trades'] = total_trades
        context['total_sales'] = total_sales
        context['appointed'] = appointed
        context['traded'] = traded
        return context

class AdminInventory(TemplateView):
    template_name = 'app/admin/admin_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        categories = Category.objects.all()
        
        category_filter = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        if category_filter:
            products = products.filter(category_name__id=category_filter)
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        context['products'] = products
        context['categories'] = categories
        context['category_filter'] = category_filter
        context['search_query'] = search_query
        return context

class AdminProduct(TemplateView):
    template_name = 'app/admin/admin_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()

        search_query = self.request.GET.get('search', '').strip()
        category_filter = self.request.GET.get('category', '').strip()
        brand_filter = self.request.GET.get('brand', '').strip()
        products = Product.objects.all()

        if search_query:
            products = products.filter(
                Q(category_name__category_name__icontains=search_query) |
                Q(brand__brand__icontains=search_query) |
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(price__icontains=search_query) |
                Q(stock__icontains=search_query)
            )
        if category_filter:
            products = products.filter(category_name__id=category_filter)
        if brand_filter:
            products = products.filter(brand__id=brand_filter)
        
        # Use the filtered products, not all products
        context['products'] = products.prefetch_related('images').all()
        context['search_query'] = search_query
        context['category_filter'] = category_filter
        context['brand_filter'] = brand_filter
        
        
        context['form'] = Add()
        context['category_form'] = AddCategory
        context['brand_form'] = AddBrand
        context['variant_form'] = AddVariantForm
        context['search_query'] = search_query
        context['category_filter'] = category_filter
        context['brand_filter'] = brand_filter
        return context

class AdminAppointment(TemplateView):
    template_name = 'app/admin/admin_appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        appointments = Appointment.objects.all().order_by('-created_at')

        if search_query:
            appointments = appointments.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if status_filter:
            appointments = appointments.filter(status=status_filter)

        context['appointments'] = appointments
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        return context

class AdminSellingAppointment(TemplateView):
    template_name = 'app/admin/admin_selling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        sellings = Selling.objects.all().order_by('-selling_at')

        if search_query:
            sellings = sellings.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if status_filter:
            sellings = sellings.filter(status=status_filter)

        context['sellings'] = sellings
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        return context