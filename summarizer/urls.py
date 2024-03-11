from django.urls import path, re_path, include
from . import views
from django.conf import settings

# Define your non-i18n patterns
non_i18n_patterns = [
    path("home2/", views.main, name="home2"),
    path("summary/", views.summary),
    path("blog/", views.blog, name="blog"),
    path("pricing/", views.pricing, name="pricing"),
    path("", views.home2, name="home"),
    path("TermsandConditions/", views.termsandconditions, name="termsandConditions"),
    path("PrivacyPolicy/", views.privacypolicy, name="privacypolicy"),
    path('logout/', views.custom_logout, name='custom_logout'),
    path("about/", views.about, name="about"),
    path("accounts/signup/", views.SignupView.as_view(), name="account_signup"),
    path("accounts/login/", views.LoginView.as_view(), name="account_login"),
    path(
        "accounts/confirm-email/<str:key>/",
        views.CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "accounts/password/reset/",
        views.CustomPasswordResetView.as_view(),
        name="account_reset_password",
    ),
    path("blog/<slug:slug>", views.blog_detail, name="blog_detail"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
]

# Check if the locale middleware is enabled
if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
    urlpatterns = [
        re_path(r'^(?P<language_code>{})/'.format('|'.join([lang[0] for lang in settings.LANGUAGES])),
                include((non_i18n_patterns, 'summy_saas'))),
        path('', include((non_i18n_patterns, 'summY_saas'))),
    ]
else:
    urlpatterns = non_i18n_patterns
