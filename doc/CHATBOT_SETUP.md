# AI Chatbot Setup Guide

## Overview
The Virtual Cafe now includes an AI-powered chatbot widget that appears in the bottom-right corner of every page. The chatbot uses Google's Gemini API to provide intelligent responses to user queries.

## Features
- 💬 Chat widget visible on all pages
- 🎨 Beautiful UI with dark mode support
- ⌨️ Send messages via Enter key
- 💾 Message history saved in browser
- 🌍 Responsive design for mobile devices
- ✨ Smooth animations and transitions

## Installation

### 1. Install Google Generative AI Package
The package has already been installed via pip:
```bash
pip install google-generativeai
```

If you need to install it manually:
```bash
pip install google-generativeai
```

### 2. Set Up Gemini API Key

#### Get Your API Key:
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Get API Key" button
3. Create a new API key in the Google Cloud Console
4. Copy your API key

#### Configure Environment Variable:
Add your API key to your environment variables:

**On Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**On Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**On Windows (Permanent):**
1. Right-click "This PC" or "My Computer"
2. Select "Properties"
3. Click "Advanced system settings"
4. Click "Environment Variables"
5. Click "New" under "User variables"
6. Variable name: `GEMINI_API_KEY`
7. Variable value: `your-api-key-here`
8. Click OK and restart your terminal/IDE

**On Linux/Mac (.bashrc or .zshrc):**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Using .env file (Recommended for Development):**
Create a `.env` file in your project root:
```
GEMINI_API_KEY=your-api-key-here
```

Then in your Python code (already configured in settings):
```python
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

## How It Works

### Backend (Django)
- **File:** [chatbot/views.py](chatbot/views.py)
- **Endpoint:** `/api/chatbot/`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "message": "Your question here"
  }
  ```
- **Response:**
  ```json
  {
    "reply": "AI response here"
  }
  ```

### Frontend (JavaScript)
- **CSS:** [static/css/chatbot.css](../static/css/chatbot.css)
- **JS:** [static/js/chatbot.js](../static/js/chatbot.js)
- **Integration:** Added to [templates/base.html](../templates/base.html)

### Features Implemented:
1. **Widget Toggle** - Click the button to open/close chat
2. **Message History** - Previous messages saved in localStorage
3. **Dark Mode Support** - Widget respects site theme
4. **Responsive Design** - Works on mobile and desktop
5. **Error Handling** - Graceful error messages
6. **CSRF Protection** - Secure POST requests

## Customization

### Change Widget Position
Edit [static/css/chatbot.css](../static/css/chatbot.css):
```css
.chatbot-widget-container {
    position: fixed;
    bottom: 20px;  /* Change this for vertical position */
    right: 20px;   /* Change this for horizontal position */
}
```

### Change Widget Colors
Modify the gradient in chatbot.css:
```css
.chatbot-toggle-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change these hex colors to your preferred colors */
}
```

### Change Widget Icon
Edit [static/js/chatbot.js](../static/js/chatbot.js):
```javascript
const toggleBtn = `<button class="chatbot-toggle-btn" title="Open AI Assistant">💬</button>`;
// Change 💬 to any emoji you prefer
```

### Disable Widget on Specific Pages
In the page template, add before `{% block extra_js %}`:
```html
<script>
    window.disableChatbot = true;
</script>
```

Then update chatbot.js to check this variable.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'google'"
**Solution:** Reinstall the package:
```bash
pip install google-generativeai --force-reinstall
```

### Issue: "Chatbot service is not configured"
**Solution:** Set the GEMINI_API_KEY environment variable and restart the server.

### Issue: Chatbot widget doesn't appear
**Solutions:**
1. Check browser console for JavaScript errors (F12)
2. Make sure chatbot CSS and JS files are loaded (check Network tab)
3. Verify `chatbot` app is in INSTALLED_APPS in settings.py
4. Clear browser cache and refresh page

### Issue: API returns rate limit error
**Solution:** Google's free tier has rate limits. Wait a few minutes or upgrade your plan at [Google AI Studio](https://aistudio.google.com).

## API Documentation

### Available Endpoints
- `POST /api/chatbot/` - Send a message and get a response

### Request Format
```json
{
  "message": "Your question or statement"
}
```

### Response Format
Success:
```json
{
  "reply": "AI generated response"
}
```

Error:
```json
{
  "reply": "Error message"
}
```

## Security Considerations

1. **API Key Security:**
   - Never commit your `.env` file to version control
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **CSRF Protection:**
   - The chatbot endpoint is CSRF-exempt for POST requests
   - In production, consider implementing additional security

3. **Input Validation:**
   - Messages are escaped to prevent XSS attacks
   - Backend validates message length and format

## Performance Tips

1. **Message Caching:** Messages are cached in localStorage
2. **Lazy Loading:** Widget loads only when needed
3. **Debouncing:** Consider adding debouncing for rapid messages
4. **API Optimization:** Gemini API responses are fast (usually < 2 seconds)

## Future Enhancements

- [ ] Message database storage
- [ ] User-specific conversation history
- [ ] Multiple AI models support
- [ ] Conversation export feature
- [ ] Rate limiting
- [ ] Admin panel for chatbot settings
- [ ] Typing indicators
- [ ] Suggested responses

## Files Modified/Created

### New Files:
- `chatbot/` - New Django app
- `static/css/chatbot.css` - Widget styling
- `static/js/chatbot.js` - Widget JavaScript

### Modified Files:
- `virtualcafe/settings.py` - Added 'chatbot' to INSTALLED_APPS
- `virtualcafe/urls.py` - Added chatbot URL configuration
- `templates/base.html` - Included chatbot CSS and JS
- `requirements.txt` - Added google-generativeai dependency

## Support

For issues or questions, check:
1. Django Channels documentation
2. Google Generative AI documentation
3. Browser console for errors
4. Django debug toolbar for backend issues

---

**Version:** 1.0  
**Last Updated:** February 4, 2026
