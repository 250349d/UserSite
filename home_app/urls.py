from django.urls import path
from django.views.generic import TemplateView

app_name = 'home_app'
urlpatterns = [
    # homepage
    path('', TemplateView.as_view(template_name='home_app/homepage.html')),
]
