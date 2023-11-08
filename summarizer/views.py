from django.shortcuts import render
from django.http import JsonResponse
from .helpers import summarizer
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


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
