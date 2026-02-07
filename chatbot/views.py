from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
import google.generativeai as genai

# API key directly
GEMINI_API_KEY = 'AIzaSyAQSDQbkczqyxypaD6uB5x7qicQ7RqCQOI'

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """
    API endpoint for chatbot messages.
    Expects JSON with 'message' field and returns JSON with 'reply' field.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'reply': 'Please provide a message.'
            }, status=400)

        if not model or not GEMINI_API_KEY:
            return JsonResponse({
                'reply': 'Chatbot service is not configured. Please contact support.'
            }, status=500)
        
        # Get response from Gemini
        try:
            response = model.generate_content(user_message)
            bot_reply = response.text if response.text else 'I could not generate a response. Please try again.'

        except Exception as e:
            print(f"[Chatbot] Gemini API Error: {str(e)}")
            bot_reply = 'Sorry, I encountered an error processing your request. Please try again.'

        return JsonResponse({
            'reply': bot_reply
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'reply': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        print(f"[Chatbot] Server Error: {str(e)}")
        return JsonResponse({
            'reply': 'An error occurred. Please try again later.'
        }, status=500)