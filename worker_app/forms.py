from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .models import CustomUser

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label='名前')
    last_name = forms.CharField(max_length=150, required=True, label='名字')
    email = forms.EmailField(max_length=254, required=True, label='メールアドレス')
    birthdate = forms.DateField(required=True, label='生年月日', widget=forms.DateInput(attrs={'type': 'date'}))
    post_code = forms.CharField(max_length=15, required=True, label='郵便番号')
    address = forms.CharField(max_length=150, required=True, label='住所')
    street_address = forms.CharField(max_length=150, required=True, label='番地以下')
    telephone_number = forms.CharField(max_length=15, required=True, label='電話番号')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = '8文字以上で、文字と数字を含める必要があります。'
        self.fields['password2'].help_text = '確認のため、同じパスワードを入力してください。'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認用）'

        # パスワードバリデーションメッセージの日本語化
        self.error_messages.update({
            'password_mismatch': "パスワードが一致しません。",
        })

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'birthdate', 'post_code', 'address', 'street_address', 'telephone_number', 'password1', 'password2')
