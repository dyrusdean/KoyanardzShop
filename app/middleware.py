from django.shortcuts import redirect
from django.urls import reverse

class OAuthProfileCompletionMiddleware:
    """
    Middleware to redirect users with incomplete OAuth profiles to complete setup.
    Users who signed up with Google OAuth must complete their profile before accessing other pages.
    """
    
    # URLs that should be accessible even with incomplete OAuth profile
    ALLOWED_PATHS = [
        '/complete-oauth-profile/',
        '/logout/',
        '/accounts/',  # Allow allauth URLs
        '/admin/',     # Allow admin
        '/static/',    # Allow static files
        '/media/',     # Allow media files
        '/api/',       # Allow API endpoints
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and has pending OAuth profile
        if request.user.is_authenticated and hasattr(request.user, 'is_oauth_pending') and request.user.is_oauth_pending:
            # Check if current path is in allowed paths
            is_allowed = any(request.path.startswith(allowed) for allowed in self.ALLOWED_PATHS)
            
            if not is_allowed:
                # Redirect to OAuth profile completion page
                return redirect('complete_oauth_profile')
        
        response = self.get_response(request)
        return response
