"""
URL configuration for UserSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('homepage/', include("home_app.urls")),
    path('notification/', include("notification_app.urls")),
    path('send-contact/', include("send_contact_app.urls")),
    path('signup/', include('signup_app.urls')),
    path('client/', include('client_app.urls')),
    path('userdelete/', include('userdelete_app.urls')),
    path('worker/', include('worker_app.urls')),
    path('passreset/', include('passreset_app.urls')),
    path('passchange/', include('passchange_app.urls')),
    path('login-app/', include('login_app.urls')),
    path('edit-user-information/', include('edit_user_information_app.urls')),
    path('chat/', include('chat_app.urls')),
]
