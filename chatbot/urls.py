from django.urls import path
from . import views

urlpatterns = [
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]
