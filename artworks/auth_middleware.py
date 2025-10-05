"""
Basic authentication middleware for site-wide password protection.
Remove this when ready to go public.
"""
import base64
from django.http import HttpResponse


class BasicAuthMiddleware:
    """Password protect the entire site during testing"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip password protection for specific paths
        exempt_paths = [
            '/admin',
            '/accounts/verify/',  # Allow email verification
        ]
        
        # Check if current path should be exempt
        for path in exempt_paths:
            if request.path.startswith(path):
                return self.get_response(request)
        
        # Check Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Basic '):
            try:
                auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = auth_decoded.split(':', 1)
                
                # Change these credentials!
                if username == 'demo' and password == 'JerseyArt2025':
                    return self.get_response(request)
            except:
                pass
        
        # Return login prompt
        response = HttpResponse('Authentication Required', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Jersey Artwork - Testing"'
        return response