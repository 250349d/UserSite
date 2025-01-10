from . import views
from django.urls import path

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    path('other/', views.other_view, name='other'),
    path('passwordchange/', views.password_change_view, name='passwordchange'),
    path('delete/', views.delete_view, name='delete'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
]
