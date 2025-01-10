from django.db import models
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

"""
利用者モデル（CustomUser）を定義．
また，UserManager クラスの username に関係するフィールドを修正．
"""
#アカウントが削除された際、削除済みのユーザに置き換えるための関数
def get_sentinel_user():
    return CustomUser.objects.get_or_create(
            first_name = "None",
            last_name = "None",
            birthdate = '0000-00-00',
            post_code = "None",
            address = "None",
            street_address = "None",
            email = "none@example.com",
            telephone_number = "None"
    )[0]

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    first_name = models.CharField(
        verbose_name="名前",
        max_length=150
    )
    last_name = models.CharField(
        verbose_name="名字",
        max_length=150
    )
    birthdate = models.DateField(
        verbose_name="生年月日"
    )
    post_code = models.CharField(
        verbose_name="郵便番号",
        max_length=15
    )
    address = models.CharField(
        verbose_name="住所",
        max_length=150
    )
    street_address = models.CharField(
        verbose_name="番地以下",
        max_length=150
    )
#    email = models.EmailField(_("email address"), blank=True)
    email = models.EmailField(
#        verbose_neme="メールアドレス",
        _("email address"),
        unique=True
    )
    bank_name = models.CharField(
        verbose_name="銀行名",
        max_length=60,
        blank=True,
        null=True
    )
    branch_number = models.CharField(
        verbose_name="支店番号",
        max_length=15,
        blank=True,
        null=True
    )
    bank_account_number = models.CharField(
        verbose_name="口座番号",
        max_length=15,
        blank=True,
        null=True
    )
    telephone_number = models.CharField(
        verbose_name="電話番号",
        max_length=15,
        unique=True
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # related_nameを追加
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # related_nameを追加
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "birthdate", "post_code", "address", "street_address", "telephone_number"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        #abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

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
