from django.urls import path
from . import views

app_name = 'send_contact_app'
urlpatterns = [
    path('', views.send_contact_view, name='send_contact'),
]
