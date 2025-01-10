from django.urls import path
from .views import send_contact_view

urlpatterns = [
    path('', send_contact_view, name='send_contact'),
]