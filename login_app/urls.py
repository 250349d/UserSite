from . import views
from django.urls import path

app_name = 'login_app'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
