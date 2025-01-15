from django.urls import path
from . import views

app_neme = 'edit_user_information_app'
urlpatterns = [
    path('edit/', views.edit_view, name='edit'),
]
