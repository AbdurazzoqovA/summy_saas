from django.urls import is_valid_path

class RemoveLanguagePrefixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language_prefix = '/' + request.LANGUAGE_CODE + '/'
        path_info = request.path_info

        if path_info.startswith(language_prefix) and is_valid_path(path_info[len(language_prefix):]):
            request.path_info = path_info[len(language_prefix):]

        response = self.get_response(request)
        return response
