# summy_saas/middleware.py

from django.utils.translation import get_language

class RemoveLanguagePrefixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the language is set to the default language (English)
        if get_language() == 'en' and request.path.startswith('/en/'):
            request.path_info = request.path_info[3:]

        response = self.get_response(request)
        return response
