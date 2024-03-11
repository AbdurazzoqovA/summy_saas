from django.conf import settings
from django.core.urlresolvers import is_valid_path
from django.http import HttpResponseRedirect
from django.middleware.locale import LocaleMiddleware
from django.utils.translation import (
    activate as activate_language,
    deactivate as deactivate_language,
    get_language,
    get_language_from_path
)
from django.utils.cache import patch_vary_headers

 
class SimpleLocaleMiddleware(LocaleMiddleware):
 
    def process_request(self, request):
        if self.is_language_prefix_patterns_used():
            lang_code = get_language_from_path(request.path_info)
            if lang_code == settings.LANGUAGE_CODE:
                activate_language(lang_code)
                request.LANGUAGE_CODE = get_language()
                # We have to ignore the prefix
                prefixless_path = "/" + "/".join(request.path.split("/")[2:])
                urlconf = getattr(request, 'urlconf', None)
                valid_path = is_valid_path(prefixless_path, urlconf)
                if not valid_path and settings.APPEND_SLASH and not prefixless_path.endswith('/'):
                    valid_path = is_valid_path("%s/" % prefixless_path, urlconf)
                if valid_path:
                    full_path = "/" + "/".join(request.get_full_path().split("/")[2:])
                    prefixless_path = "%s://%s%s" % (
                        request.is_secure() and 'https' or 'http',
                        request.get_host(),
                        full_path
                    )
                    return HttpResponseRedirect(prefixless_path)
            else:
                lang_code = lang_code or settings.LANGUAGE_CODE
                activate_language(lang_code)
                request.LANGUAGE_CODE = get_language()

    def process_response(self, request, response):
        # This is a straight up copy of the current LocaleMiddleware.process_response.
        # only change is that we check that the current language is not the default language before redirecting.
        # This way we avoid an infinite loop.
        language = get_language()
        is_default = language == settings.LANGUAGE_CODE
        is_404 = response.status_code == 404
        if (is_404 and not get_language_from_path(request.path_info)
            and self.is_language_prefix_patterns_used() and not is_default):
            urlconf = getattr(request, 'urlconf', None)
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            if (not path_valid and settings.APPEND_SLASH
                    and not language_path.endswith('/')):
                path_valid = is_valid_path("%s/" % language_path, urlconf)

            if path_valid:
                language_url = "%s://%s/%s%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(), language, request.get_full_path())
                return HttpResponseRedirect(language_url)
        deactivate_language()

        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response