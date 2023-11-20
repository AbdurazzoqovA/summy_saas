from django.shortcuts import render, redirect
from django.http import JsonResponse
from .helpers import summarizer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib import messages
import json
from allauth.account.views import ConfirmEmailView
from allauth.account.views import SignupView as AllauthSignupView
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.views import PasswordResetView as AllauthPasswordResetView

User = get_user_model()

def main(request):
    return render(request, "front/main.html")


@csrf_exempt
def summary(request):
    if request.method == "POST":
        # Parse the request body as JSON
        data = json.loads(request.body)
        text = data.get("text")
        temp_text = text.replace("\n", " ").replace(" ", "")

        if len(text) < 10:
            return JsonResponse({"error": "plase provide more text"}, status=400)
        elif "SampleTextPasteText" == temp_text:
            return JsonResponse({"error": "plase provide more text"}, status=400)

        summary = summarizer(
            text
        )  # Ensure your summarizer function is properly defined
        return JsonResponse({"summary": summary})

class SignupView(AllauthSignupView):
    template_name = 'account/signup.html'
    def form_invalid(self, form):
        errors = form.errors.values()
        custom_error = "Custom error message."
        return render(self.request, self.template_name, {'form': form, 'errors': errors, 'custom_error': custom_error})
    
class CustomConfirmEmailView(ConfirmEmailView):
    def get_success_url(self):
        return 'account/login.html'

class LoginView(AllauthLoginView):
    template_name = 'account/login.html'

    def form_invalid(self, form):
        errors = form.errors.values()
        custom_error = "Invalid login credentials. Please try again."
        return render(self.request, self.template_name, {'form': form, 'errors': errors, 'custom_error': custom_error})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful.')
        return response


class CustomPasswordResetView(AllauthPasswordResetView):
    template_name = 'account/password_reset.html'
