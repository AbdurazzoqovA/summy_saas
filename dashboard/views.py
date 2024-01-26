from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from payments.models import Subscription, WordCountTracker
from .models import Documents
from django.core.paginator import Paginator
from django.db.models import Avg
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
import uuid
import stripe
from django.conf import settings
import datetime
from django.contrib.auth import logout
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def get_dashboard_data(user):
    data = {
        "subscription_name": "No Active Subscription",
        "available_words": 0,
        "used_words": 0,
        "used_percentage": 0,
    }

    active_subscription = Subscription.objects.filter(user=user, is_active=True).first()
    if active_subscription:
        data["subscription_name"] = active_subscription.plan_type.capitalize()
        data["subscrioption_price"] = active_subscription.price_in_cents / 100
        data["subscrioption_id"] = active_subscription.stripe_subscription_id

        try:
            data["next_due_date"] = active_subscription.end_date.date
        except:
            data["next_due_date"] = active_subscription.end_date
    word_count_tracker = WordCountTracker.objects.filter(subscription__user=user).last()
    documents_count = Documents.objects.filter(user=user).count()
    average_words_per_document = Documents.objects.filter(user=user).aggregate(
        average_words=Avg("words_used")
    )["average_words"]

    # You might want to handle the case where there are no documents
    if average_words_per_document is None:
        average_words_per_document = 0

    if word_count_tracker:
        data["available_words"] = word_count_tracker.words_remaining
        data["words_purchased"] = word_count_tracker.words_purchased
        data["used_words"] = word_count_tracker.words_used
        data["documents_count"] = documents_count
        data["average_words_per_document"] = round(average_words_per_document)
        if word_count_tracker.words_purchased > 0:
            data["used_percentage"] = (
                word_count_tracker.words_used / word_count_tracker.words_purchased
            ) * 100

    return data


@login_required
def index(request):
    context = get_dashboard_data(request.user)
    recent_documents = Documents.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:5]
    if recent_documents.count() > 0:
        context["recent_documents"] = recent_documents
    else:
        context["recent_documents"] = None
    context["recent_documents"] = recent_documents
    return render(request, "dashboard/dashboard.html", context)


def get_stripe_customer_id_by_email(user_email):
    customers = stripe.Customer.list(email=user_email).auto_paging_iter()
    for customer in customers:
        # Assuming one email is associated with only one customer
        return customer.id
    return None


def get_formated_invoices(customer_id):
    formatted_invoices = []
    invoices = stripe.Invoice.list(customer=customer_id)
    for invoice in invoices.get("data", []):
        # Subscription Name
        subscription_name = (
            invoice["lines"]["data"][0]["description"]
            if invoice["lines"]["data"]
            else "N/A"
        )

        # Payment Date (convert from Unix timestamp to human-readable date)
        payment_date = datetime.datetime.fromtimestamp(invoice["created"]).strftime(
            "%Y-%m-%d"
        )

        # Total (convert from smallest currency unit to standard format, e.g., cents to dollars)
        total = invoice["total"] / 100.0

        # Status
        status = invoice["status"]

        formatted_invoices.append(
            {
                "subscription_name": subscription_name.replace("1 ×", ""),
                "payment_date": payment_date,
                "total": total,
                "status": status,
                "invoice_pdf": invoice["invoice_pdf"],
            }
        )
    return formatted_invoices


@login_required
def profile(request):
    user_email = request.user.email
    customer_id = get_stripe_customer_id_by_email(user_email)

    if customer_id:
        invoices = get_formated_invoices(customer_id)
        # Or use stripe.Charge.list(customer=customer_id) if you want to list charges
    else:
        invoices = []
    context = get_dashboard_data(request.user)
    context["invoices"] = invoices
    context["subscription_name_period"] = context["subscription_name"].replace("ly", "")
    return render(request, "dashboard/profile.html", context=context)


@login_required
def edit_profile(request):
    context = get_dashboard_data(request.user)
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        country = request.POST.get("country")
        is_checked = "check_box" in request.POST

        if is_checked:
            checked = True
        else:
            checked = False
        user = request.user
        user.fullname = fullname
        user.country = country
        user.does_email_receive = checked
        user.save()
        return redirect("profile")

    return render(request, "dashboard/edit_profile.html", context=context)


@login_required
def documents(request):
    # Fetch search query and sort parameters from the request
    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "-created_at")  # Default sort is by created_at

    # Filter and sort documents based on the search query and sort parameter
    documents = Documents.objects.filter(
        user=request.user,
        input_text__icontains=search_query,  # Assuming you are searching by document name
    ).order_by(sort_by)

    # Add Pagination
    paginator = Paginator(documents, 15)  # Show 10 documents per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"documents": page_obj}
    return render(request, "dashboard/documents.html", context=context)


@login_required
def document_detail(request, document_id):
    try:
        # Make sure we have a valid UUID
        uuid.UUID(document_id)
    except ValueError:
        raise Http404("Invalid document ID format.")

    # Retrieve the document, making sure it exists and belongs to the current user
    try:
        document = Documents.objects.get(document_id=document_id, user=request.user)
    except Documents.DoesNotExist:
        raise Http404("Document not found.")

    # If the user is not the owner of the document, raise PermissionDenied
    if document.user != request.user:
        raise PermissionDenied

    # Prepare the data to be returned as JSON
    data = {
        "input_text": document.input_text,
        "output_text": document.output_text,
        "created_at": document.created_at.isoformat(),
        "words_used": document.words_used,
        "purpose": document.purpose,
        "level": document.level,
        "readibility": document.readibility,
        "document_id": str(document.document_id),  # Convert UUID to string
    }

    return JsonResponse(data)


@login_required
def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def text_editor(request):
    return render(request, "dashboard/editor.html")


@login_required
def generate_text(request):
    if request.method == "POST":
        # Parse JSON data from the request body
        data = json.loads(request.body)
        topic = data.get("topic")
        tone = data.get("tone")
        keywords = data.get("keywords")
        language = data.get("language")
        content_type = data.get("content_type")
        min_words_count = data.get("min_words_count")
        max_words_count = data.get("max_words_count")
        user = request.user
        document_id = uuid.uuid4()
        # Call your custom text generation function
        subscrioption = Subscription.objects.filter(user=request.user).last()

        if (
            subscrioption.is_active == False
            or subscrioption.plan_type == Subscription.FREE
        ):
            return JsonResponse({"error": "Upgrade required"}, status=400)
        result = generate_content(content_type, topic, tone, keywords, language)

        # Return the result as JSON
        return JsonResponse({"result": result, "document_id": str(document_id)})


@login_required
def extend_text_view(request):
    if request.method == "POST":
        # Parse JSON data from the request body
        data = json.loads(request.body)
        text = data.get("text")
        tone = data.get("tone")
        keywords = data.get("keywords")
        language = data.get("language")
        min_words_count = data.get("min_words_count")
        max_words_count = data.get("max_words_count")

        subscrioption = Subscription.objects.filter(user=request.user).last()

        if (
            subscrioption.is_active == False
            or subscrioption.plan_type == Subscription.FREE
        ):
            return JsonResponse({"error": "Upgrade required"}, status=400)

        # Call your custom text generation function
        result = extend_text(
            text, tone, keywords, language, max_words_count, min_words_count
        )

        return JsonResponse({"result": result})


def stye_view(request):
    return render(request, "dashboard/style.html")
