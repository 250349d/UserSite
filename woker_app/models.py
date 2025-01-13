from django.db import models
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
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

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
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
    first_name = models.CharField(verbose_name="名前", max_length=150)
    last_name = models.CharField(verbose_name="名字", max_length=150)
    birthdate = models.DateField(verbose_name="生年月日")
    post_code = models.CharField(verbose_name="郵便番号", max_length=15)
    address = models.CharField(verbose_name="住所", max_length=150)
    street_address = models.CharField(verbose_name="番地以下", max_length=150)
    email = models.EmailField(_("email address"), unique=True)
    bank_name = models.CharField(verbose_name="銀行名", max_length=60, blank=True, null=True)
    branch_number = models.CharField(verbose_name="支店番号", max_length=15, blank=True, null=True)
    bank_account_number = models.CharField(verbose_name="口座番号", max_length=15, blank=True, null=True)
    telephone_number = models.CharField(verbose_name="電話番号", max_length=15, unique=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "birthdate", "post_code", "address", "street_address", "telephone_number"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

def get_sentinel_user():
    return CustomUser.objects.get_or_create(
        first_name="None",
        last_name="None",
        birthdate='2000-01-01',
        post_code="None",
        address="None",
        street_address="None",
        email="none@example.com",
        telephone_number="None"
    )[0]

class Task(models.Model):
    client = models.ForeignKey(
        CustomUser,
        on_delete=models.SET(get_sentinel_user),
        related_name='client_tasks',
        verbose_name="クライアント",
    )
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET(get_sentinel_user),
        related_name='worker_tasks',
        null=True,
        verbose_name="配達員",
    )
    title = models.CharField(
        max_length=60,
        verbose_name="依頼件名",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
        verbose_name="注文した時間",
    )
    limit_of_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="配達期限時間",
    )
    status = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="配達ステータス",
    )
    shop_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="店舗名",
    )
    delivery_completion_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="配達完了時間",
    )
    shop_post_code = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="店舗の郵便番号",
    )
    shop_address = models.CharField(
        max_length=150,
        verbose_name="店舗の住所",
    )
    shop_street_address = models.CharField(
        max_length=150,
        verbose_name="店舗の番地",
    )

    def __str__(self):
        return self.title

class Transaction(models.Model):
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='transaction',
        verbose_name="関連するタスク"
    )
    total_cost = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="合計金額"
    )
    courier_reward_amount = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="給料"
    )
    delivery_fee = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="配達手数料"
    )
    payment_fee = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="サービス代金支払い日付"
    )
    courier_item_payment_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="商品代金支払い日付"
    )
    courier_reward_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="報酬支払日付"
    )

    def __str__(self):
        return f"Transaction {self.id} - Total Cost: {self.total_cost}"

class Order(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="商品"
    )
    product_name = models.CharField(
        max_length=150,
        verbose_name="商品名"
    )
    price = models.IntegerField(
        verbose_name="単価"
    )
    quantity = models.IntegerField(
        verbose_name="個数"
    )
    notes = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="備考"
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class Request(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="申請"
    )
    time = models.DateTimeField(verbose_name="申請時間")
    price = models.IntegerField(verbose_name="申請金額")
    status = models.CharField(
        max_length=1,
        verbose_name="申請ステータス"
    )

    def __str__(self):
        return f"Request {self.id} for Task {self.task.id}"