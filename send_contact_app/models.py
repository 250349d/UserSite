from django.db import models
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

CustomUser = get_user_model()

def get_sentinel_user():
    return CustomUser.objects.get_or_create(
            first_name = "None",
            last_name = "None",
            birthdate = '0001-01-01',
            post_code = "None",
            address = "None",
            street_address = "None",
            email = "none@example.com",
            telephone_number = "None"
    )[0]

class Contact(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET(get_sentinel_user),
        verbose_name="ユーザーID"
    )
    title = models.CharField(
        max_length=60,
        verbose_name="件名",
        blank=False,
        null=True
    )
    content = models.TextField(
        verbose_name="本文",
        blank=False,
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name="問い合わせ日時",
        auto_now_add=True,
        blank=True,
        null=True
    )
