from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from google.genai import types

# Get API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Initialize Gemini client
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


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

        if not client or not GEMINI_API_KEY:
            return JsonResponse({
                'reply': 'Chatbot service is not configured. Please contact support.'
            }, status=500)
        
        # Get response from Gemini with optimized settings
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    top_p=0.95,
                )
            )
            
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
