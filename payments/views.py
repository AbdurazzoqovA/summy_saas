from django.shortcuts import render, redirect

# Create your views here.
# views.py
import datetime
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from summarizer.models import User
from payments.models import Subscription, WordCountTracker
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
import json
from django.utils import timezone
from django.db.models import F
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required

# from common.telegram_sender import send_telegram_message


def calculate_price(plan_type: str, word_count: int):
    # Validate plan_type
    valid_plan_types = ["monthly", "yearly", "enterprise"]
    if plan_type.lower() not in valid_plan_types:
        raise ValueError(
            f"Invalid plan type: {plan_type}. Valid plan types are {valid_plan_types}."
        )

    # Validate word_count
    if not isinstance(word_count, int) or word_count <= 0:
        raise ValueError("Word count must be a positive integer.")

    # Define minimum word counts for each plan to prevent unrealistic low word counts
    min_word_counts = {
        "monthly": 1000000,  # Example: 20,000 words minimum for monthly
        "yearly": 10000000,  # Example: 20,000 words minimum for yearly
        # Example: 500,000 words minimum for enterprise
    }

    if word_count < min_word_counts[plan_type.lower()]:
        raise ValueError(
            f"Word count for {plan_type} plan must be at least {min_word_counts[plan_type.lower()]}."
        )

    # Price calculation
    if plan_type.lower() == "monthly":
        price = 995
        plan = "month"
    elif plan_type.lower() == "yearly":
        price = 5995
        plan = "year"
        

    return round(price, 2), plan, word_count


# Import your models

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Return a 401 Unauthorized response or a custom JSON response
            return  HttpResponseForbidden('User not authenticated')
        # Retrieve the user and their subscription plan details
        user = User.objects.get(email=request.user.email)
        # Example: retrieve plan details (word count, price) from the request
        # Adjust this part based on how you store and retrieve plan details
        data = json.loads(request.body)

        plan_type = data.get("plan_type")
        if plan_type == "monthly":
            word_count = 1000000
        elif plan_type == "yearly":
            word_count = 10000000

        price, plan, word_count = calculate_price(
            plan_type, word_count
        )  # Implement this function based on your pricing logic

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=user.email,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "recurring": {"interval": plan},
                            "product_data": {
                                "name": f"{plan_type.capitalize()} Plan - {word_count} Words",
                            },
                            "unit_amount": int(
                                price 
                            ),  # Stripe expects the amount in cents
                        },
                        "quantity": 1,
                    },
                ],
                metadata={"word_count": word_count, "plan_type": plan_type},
                mode="subscription",
                success_url="https://boostchats.com/",
                cancel_url="https://boostchats.com/",
            )
            return JsonResponse({"id": checkout_session.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def cancel_stripe_subscription(subscription_id):
    try:
        stripe.Subscription.delete(subscription_id)
    except stripe.error.StripeError as e:
        # Handle Stripe API error
        print(f"Stripe API error: {e}")
        # Depending on your requirement, you might want to log this error or take additional actions


def handle_checkout_session(session):
    customer_email = session.get("customer_email")
    subscription_id = session.get("subscription")
    stripe_customer_id = session.get("customer")
    
    try:
        user = User.objects.get(email=customer_email)

    except User.DoesNotExist:
        # Handle user not found
        return HttpResponse(status=400)

    # Retrieve the subscription from Stripe
    stripe_subscription = stripe.Subscription.retrieve(subscription_id)

    # Calculate subscription duration based on Stripe's interval
    word_count = int(session.get("metadata", {}).get("word_count", 0))
    plan_type = session.get("metadata", {}).get("plan_type")
    interval = (
        stripe_subscription.plan.interval
        if stripe_subscription and stripe_subscription.plan
        else None
    )

    start_date = timezone.now()
    end_date = calculate_end_date(start_date, interval)

    # Check for existing active subscription and carry over unused words
    existing_subscription = Subscription.objects.filter(
        user=user, is_active=True
    ).first()
    total_words_count = word_count
    if existing_subscription:
        # Renewal: carry over unused words
        if existing_subscription.plan_type != "free":
            cancel_stripe_subscription(existing_subscription.stripe_subscription_id)
        existing_subscription.is_active = False
        existing_subscription.actual_end_date = timezone.now()
        existing_subscription.save()
        total_words_count = word_count + get_unused_words(existing_subscription)

    # Update or create the subscription record in your database
    subscription = Subscription.objects.create(
        user=user,
        plan_type=plan_type,
        price_in_cents=stripe_subscription.plan.amount,
        stripe_subscription_id=subscription_id,
        is_active=True,
        start_date=start_date,
        end_date=end_date,
        word_count=word_count,
    )

    # Update word count tracker
    WordCountTracker.objects.update_or_create(
        subscription=subscription,
        defaults={
            "words_purchased": total_words_count,
            # Reset words_used if needed, or handle it according to your logic
        },
    )
    user.stripe_customer_id = stripe_customer_id
    user.save()
    return HttpResponse(status=200)
    # Additional actions...


def calculate_end_date(start_date, interval):
    if interval == "month":
        return start_date + relativedelta(months=1)
    elif interval == "year":
        return start_date + relativedelta(years=1)
    return None


def get_unused_words(subscription):
    word_count_tracker = WordCountTracker.objects.filter(
        subscription=subscription
    ).first()
    if word_count_tracker:
        return max(
            word_count_tracker.words_purchased - word_count_tracker.words_used, 0
        )
    return 0


def handle_successful_payment(invoice):
    # Get the customer ID and subscription ID from the invoice
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
   
    # Retrieve the corresponding user and subscription in your database
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_id, user=user
        )
    except User.DoesNotExist:
        return HttpResponse(status=400)
    except Subscription.DoesNotExist:
        subscription = Subscription.objects.get(user=user).last()
        subscription_id = subscription.stripe_subscription_id

    # Update subscription details
    # For instance, you might want to update the subscription's end date
    # based on the current billing cycle of the Stripe subscription
    stripe_subscription = stripe.Subscription.retrieve(subscription_id)

    subscription.start_date = timezone.now()
    subscription.end_date = timezone.now() + relativedelta(months=1)
    subscription.save()

    # You might also want to reset or update the word count tracker for the new billing period
    WordCountTracker.objects.filter(subscription=subscription).update(
        words_purchased=F("words_purchased")
        + subscription.word_count
        # Optionally update other fields if needed
    )
    return HttpResponse(status=200)


def handle_failed_payment(invoice):
    # Handle failed payment webhook and block access to paid features
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_id, user=user
        )
    except User.DoesNotExist:
        return HttpResponse(status=400)
    except Subscription.DoesNotExist:
        return HttpResponse(status=400)

    subscription.is_active = False
    subscription.save()
    return HttpResponse(status=200)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        handle_checkout_session(session)

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        handle_successful_payment(invoice)
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        handle_failed_payment(invoice)

    # Other event types can be handled here

    return HttpResponse(status=200)


@login_required
def cancel_stripe_subscription_view(request, subscription_id):
    user = request.user
    subscrioption = Subscription.objects.filter(
        stripe_subscription_id=subscription_id, user=user
    )

    if subscrioption.exists():
        cancel_stripe_subscription(subscription_id)
        subscrioption = subscrioption.first()
        subscrioption.is_active = False
        subscrioption.actual_end_date = timezone.now()
        subscrioption.end_date = None
        subscrioption.save()
        return redirect("profile")
    else:
        return redirect("profile")
