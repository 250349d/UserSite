from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'chat_app'
urlpatterns = [
	path('', TemplateView.as_view(template_name='chat_app/chat.html'), name='chat'),
	path('event-stream/', views.event_stream, name='event-stream'),
	path('send-message/', views.send_message, name='send-message'),
]