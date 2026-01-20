"""
Firebase Authentication utilities for Django backend
"""
from django.contrib.auth import get_user_model
import os
import json
from urllib.request import urlopen
from django.core.exceptions import ValidationError

User = get_user_model()

class FirebaseAuthError(Exception):
    """Custom exception for Firebase authentication errors"""
    pass

def verify_firebase_token(token):
    """
    Verify a Firebase ID token and return the decoded token data
    
    Args:
        token: Firebase ID token from client
        
    Returns:
        dict: Decoded token data including uid, email, email_verified, etc.
        
    Raises:
        FirebaseAuthError: If token verification fails
    """
    try:
        # Get Firebase public keys
        url = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        with urlopen(url) as response:
            keys = json.load(response)
        
        # Decode the token (simplified - in production, use firebase-admin-sdk)
        # This is a basic verification approach
        import jwt
        from jwt import PyJWKClient
        
        jwks_client = PyJWKClient(url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="koyanardzshop-601f8",  # Your Firebase project ID
            options={"verify_exp": True}
        )
        
        return decoded
        
    except Exception as e:
        raise FirebaseAuthError(f"Token verification failed: {str(e)}")

def get_or_create_user_from_firebase(firebase_uid, email, display_name=None):
    """
    Get or create a Django user from Firebase authentication data
    
    Args:
        firebase_uid: Firebase user ID
        email: User email
        display_name: Optional display name
        
    Returns:
        tuple: (user, created) where created is True if user was newly created
    """
    try:
        user = User.objects.get(email=email)
        return user, False
    except User.DoesNotExist:
        # Create new user
        username = email.split('@')[0]
        # Ensure unique username
        counter = 1
        base_username = username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=display_name or "",
            is_active=True  # Mark as active since email is verified by Firebase
        )
        
        return user, True
