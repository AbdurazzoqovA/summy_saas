from django.urls import path
from . import views

urlpatterns = [
    path("", views.main, name="home"),
    path("summary/", views.summary),
    path("blog/", views.blog, name="blog"),
    path("pricing/", views.pricing, name="pricing"),
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
]
