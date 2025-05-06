from django.urls import path
from .views import ChatBotView

urlpatterns = [
    path('/chat-public', ChatBotView.as_view(), name='chatbot'),
]