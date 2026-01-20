from django.db.models.signals import post_save
from django.conf import settings
import os
import requests
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
import threading
from .models import OtpToken, ProductImage, Product
import logging
import cloudinary
import cloudinary.uploader

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            # Check if this is a Google OAuth signup (no password set)
            is_google_oauth = not instance.has_usable_password()
            
            if is_google_oauth:
                # Auto-activate Google OAuth accounts - no profile completion needed
                instance.is_active = True
                instance.is_oauth_pending = False
                instance.save()
                logger.info(f"Google OAuth account created and activated for {instance.username}")
            else:
                # For normal signups, DO NOT send OTP email here
                # The register view handles OTP creation and email sending
                # Mark as inactive - will be activated after OTP verification in register view
                instance.is_active = False
                instance.save()
                logger.info(f"User {instance.username} created (inactive, OTP will be sent by register view)")


# Signal to upload ProductImage files to Cloudinary
@receiver(post_save, sender=ProductImage)
def upload_product_image_to_cloudinary(sender, instance, created, **kwargs):
    """Upload ProductImage to Cloudinary when created or updated
    
    NOTE: This signal is now mostly a no-op because cloudinary_storage backend
    handles automatic uploads when DEFAULT_FILE_STORAGE is set to MediaCloudinaryStorage.
    
    This signal only logs for debugging purposes.
    """
    if not instance.product_image:
        return
    
    # Log for debugging
    logger.debug(f"ProductImage {instance.id} saved: {instance.product_image.name}")
    
    # Check if it has a valid Cloudinary URL
    if instance.product_image.url.startswith('https://res.cloudinary.com'):
        logger.debug(f"✓ ProductImage {instance.id} already in Cloudinary: {instance.product_image.url}")


# Signal to upload Product main image to Cloudinary
@receiver(post_save, sender=Product)
def upload_product_main_image_to_cloudinary(sender, instance, created, **kwargs):
    """Upload Product main image to Cloudinary when created or updated
    
    NOTE: This signal is now mostly a no-op because cloudinary_storage backend
    handles automatic uploads when DEFAULT_FILE_STORAGE is set to MediaCloudinaryStorage.
    
    This signal only logs for debugging purposes.
    """
    if not instance.image:
        return
    
    # Log for debugging
    logger.debug(f"Product {instance.id} main image saved: {instance.image.name}")
    
    # Check if it has a valid Cloudinary URL
    if instance.image.url.startswith('https://res.cloudinary.com'):
        logger.debug(f"✓ Product {instance.id} main image already in Cloudinary: {instance.image.url}")


# Signal to upload 3D models to B2 (NOT Cloudinary)
@receiver(post_save, sender=Product)
def upload_3d_model_to_b2(sender, instance, created, **kwargs):
    """Upload 3D model to B2 (not Cloudinary) when created or updated
    
    The model_3d field should use B2Storage backend directly.
    This signal logs the upload location for debugging.
    """
    if not instance.model_3d:
        return
    
    try:
        model_url = instance.model_3d.url
        logger.info(f"Product {instance.id} 3D model URL: {model_url}")
        
        # Check storage location
        if 'backblazeb2.com' in model_url:
            logger.info(f"✓ Product {instance.id} 3D model correctly stored in B2: {model_url}")
        elif 'res.cloudinary.com' in model_url:
            logger.warning(f"✗ Product {instance.id} 3D model is in Cloudinary (should be B2): {model_url}")
        else:
            logger.info(f"ℹ Product {instance.id} 3D model location: {model_url}")
    except Exception as e:
        logger.error(f"Error checking 3D model storage location: {e}")