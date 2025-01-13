from . import views
from django.urls import path

app_name = 'userdelete_app'
urlpatterns = [
    path('', views.userdelete_view, name='userdelete'),
]
