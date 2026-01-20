from django.shortcuts import render


def csrf_failure_view(request, reason=""):
    """
    Handle CSRF token validation failures.
    Renders a user-friendly error page.
    """
    context = {
        'reason': reason,
        'debug': __import__('django.conf', fromlist=['settings']).settings.DEBUG,
    }
    return render(request, 'csrf_error.html', context, status=403)
