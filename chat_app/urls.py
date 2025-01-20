from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'chat_app'
urlpatterns = [
	path('<int:task_id>/', views.show_chat, name='chat'),
	path('<int:task_id>/event-stream/', views.event_stream, name='event-stream'),
	path('update-message/', views.update_message, name='update-message'),
	path('send-message/', views.send_message, name='send-message'),
]