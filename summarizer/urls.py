from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from . import views

urlpatterns = [
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


urlpatterns += i18n_patterns(
    *urlpatterns,
    prefix_default_language=False,
)