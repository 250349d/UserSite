from . import views
from django.urls import path

app_name = 'signup_app'
urlpatterns = [
    path('', views.signup_view, name='signup'),
]
