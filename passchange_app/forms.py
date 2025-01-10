from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CpassForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
