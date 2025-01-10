from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        #model = Contact
        model = User 
        fields = ['last_name','first_name', 'email', 'password1', 'password2', 'telephone_number', 
                  'birthdate', 'address', 'street_address'
                  ]

class LoginForm(AuthenticationForm):
    pass

class CpassForm(PasswordChangeForm):
    class Meta:
        model = User