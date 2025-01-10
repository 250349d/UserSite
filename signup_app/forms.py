from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser 
        fields = ['last_name','first_name', 'email', 'password1', 'password2', 'telephone_number', 'birthdate', 'address', 'street_address'
        ]
