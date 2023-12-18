from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "create_checkout/",
        views.CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe-webhook"),
    path(
        "cancel_subscrioption/<str:subscription_id>",
        views.cancel_stripe_subscription_view,
        name="cancel_subscrioption",
    ),
]

# payments/webhooks/stripe/