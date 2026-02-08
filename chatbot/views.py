from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from google.genai import types

# Get API key from environment variable (NEVER hardcode API keys!)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Initialize Gemini client only if API key exists
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[Chatbot] Failed to initialize Gemini client: {str(e)}")
        client = None
else:
    print("[Chatbot] WARNING: GEMINI_API_KEY not found in environment variables")


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """
    AI Tutor endpoint for educational assistance.
    Expects JSON with 'message' field and returns JSON with 'reply' field.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'reply': 'Please provide a message.'
            }, status=400)

        # Check if API key is configured
        if not GEMINI_API_KEY:
            return JsonResponse({
                'reply': '🔑 AI Assistant is not configured.\n\nTo enable the chatbot:\n1. Get a FREE API key from: https://aistudio.google.com/app/apikey\n2. Add it to your .env file: GEMINI_API_KEY=your-key-here\n3. Restart the server'
            }, status=503)
        
        # Check if client initialized successfully
        if not client:
            return JsonResponse({
                'reply': '⚠️ AI Assistant initialization failed. Please check your GEMINI_API_KEY in the .env file and restart the server.'
            }, status=503)
        
        # Educational AI Tutor System Prompt
        system_prompt = """You are an expert AI tutor and study companion in Virtual Cafe. Your role is to:

🎓 TEACHING APPROACH:
- Explain concepts clearly using examples, analogies, and step-by-step breakdowns
- Adapt to the student's level - ask if they need beginner, intermediate, or advanced explanations
- Use the Socratic method: ask guiding questions to help students discover answers
- Provide practice problems and verify understanding
- Break down complex topics into manageable chunks

📚 SUBJECT EXPERTISE:
- Mathematics (algebra, calculus, geometry, statistics)
- Sciences (physics, chemistry, biology)
- Programming (Python, JavaScript, web development)
- Languages and writing
- History, social studies, and humanities
- Test preparation (SAT, ACT, AP exams)

💡 STUDY SUPPORT:
- Create study plans and schedules
- Suggest memory techniques and learning strategies
- Provide motivational support and study tips
- Recommend practice resources
- Help with homework (guide, don't just give answers)

🗣️ COMMUNICATION STYLE:
- Friendly, encouraging, and patient
- Use emojis to make learning engaging
- Keep responses concise but comprehensive
- Always verify understanding before moving to next concepts
- DO NOT start every response with greetings like \"Hey there!\" or \"Welcome to Virtual Cafe!\"
- Jump straight to answering the question or teaching the concept

📝 FORMATTING RULES (CRITICAL - FOLLOW STRICTLY):
- ALWAYS use **bold** for EVERY question you ask the student (wrap in double asterisks **)
- Structure responses in clear, organized points using:
  • Numbered lists (1., 2., 3.) for steps or sequences
  • Emoji bullets (✓, 📌, 💡, etc.) for key points and concepts
  • NEVER use plain asterisks (*) for bullet points
- Add double line breaks (\\n\\n) between:
  • Each main section
  • Before and after lists
  • Between concept explanations
- Keep each point concise (1-2 sentences max)
- Always end with a **bold question** to check understanding

EXAMPLE FORMAT:
Here's how quadratic equations work:

📌 The standard form is: ax² + bx + c = 0

Steps to solve:
1. Identify coefficients (a, b, c)
2. Use the quadratic formula
3. Simplify to get your answer

**What part would you like me to explain in more detail?**

When a student asks about a topic, first assess their current level, then teach step-by-step using the formatting rules above."""

        # Get response from Gemini with educational tutor configuration
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_prompt}\n\nStudent Question: {user_message}",
                config=types.GenerateContentConfig(
                    temperature=0.8,  # Slightly higher for more engaging responses
                    max_output_tokens=2000,  # More tokens for detailed explanations
                    top_p=0.95,
                )
            )
            bot_reply = response.text if response.text else 'I could not generate a response. Please try again.'

        except Exception as e:
            error_str = str(e)
            print(f"[Chatbot] Gemini API Error: {error_str}")
            
            # Handle specific API errors
            if '403' in error_str and 'PERMISSION_DENIED' in error_str:
                if 'leaked' in error_str.lower():
                    bot_reply = '🚨 API Key Security Issue\n\nYour API key has been blocked because it was exposed publicly.\n\nTO FIX:\n1. Get a NEW API key: https://aistudio.google.com/app/apikey\n2. Update .env file with new key\n3. NEVER commit API keys to Git!\n4. Restart the server'
                else:
                    bot_reply = '🔒 Permission Denied\n\nThe API key is invalid or doesn\'t have proper permissions.\n\nTO FIX:\n1. Check your API key at: https://aistudio.google.com/app/apikey\n2. Update .env file with correct key\n3. Restart the server'
            elif '429' in error_str:
                bot_reply = '⏱️ Rate limit exceeded. Please wait a moment and try again.'
            elif '401' in error_str:
                bot_reply = '🔐 Authentication failed. Please check your API key in the .env file.'
            else:
                bot_reply = f'❌ AI Error: {error_str[:100]}\n\nPlease try again or check the server logs.'

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