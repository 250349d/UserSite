from . import views
from django.urls import path

app_name = 'passreset_app'
urlpatterns = [
    path('', views.passreset_view, name='passreset'),
]
