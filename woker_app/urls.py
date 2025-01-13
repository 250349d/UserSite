from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  # ログインページのURL
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('create/', views.create_request, name='create_request'),
    path('receive/', views.receive_request, name='receive_request'),
    path('confirm_request/<int:pk>/', views.confirm_request, name='confirm_request'),
    path('cancel_request/<int:pk>/', views.cancel_request, name='cancel_request'),
    path('accepted/', views.accepted_requests, name='accepted_requests'),
    path('rewards/', views.reward_check, name='reward_check'),
    path('submit_cost/<int:pk>/', views.submit_cost, name='submit_cost'),  
    path('approve_cost/<int:pk>/', views.approve_cost, name='approve_cost'),  # 新しいURLパターン
    path('requester/', views.requester_home, name='requester_home'),
    path('completed/', views.completed_requests_view, name='completed_requests'),
]
