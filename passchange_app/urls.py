from . import views
from django.urls import path

app_name = 'passchange_app'
urlpatterns = [
    path('', views.passchange_view, name='passchange'),
]
