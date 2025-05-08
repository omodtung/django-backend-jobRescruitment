from django.urls import path
from .views import ChatBotView, ChatBotDatabaseView

urlpatterns = [
    path('/chat-public', ChatBotView.as_view(), name='chat-bot-user'),
    path('/chat-admin', ChatBotDatabaseView.as_view(), name='chat-bot-admin')
]