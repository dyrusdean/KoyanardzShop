from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle SocialApp queries that return multiple objects
    when the app is linked to multiple sites (localhost + production)
    """

    def get_app(self, request, provider, client_id=None):
        """
        Get the SocialApp, preferring exact site match but falling back to any available app
        """
        try:
            # Try the default behavior first
            return super().get_app(request, provider, client_id)
        except MultipleObjectsReturned:
            # If multiple apps found, return the first one for this provider
            app = SocialApp.objects.filter(provider=provider).first()
            if app:
                return app
            # If still nothing, re-raise
            raise
