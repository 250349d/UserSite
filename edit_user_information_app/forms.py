from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    birthdate = forms.DateField(
        widget=forms.SelectDateWidget(years=[x for x in range(1900, 2024)]),
        label='生年月日'
    )
    
    class Meta:
        model = User
        fields = [
            'last_name', 'first_name', 'email', 'birthdate', 
            'telephone_number', 'post_code', 'address', 'street_address',
            'bank_name', 'branch_number', 'bank_account_number', 'password1', 'password2'
        ]
        labels = {
            'last_name': '名字',
            'first_name': '名前',
            'email': 'メールアドレス',
            'telephone_number': '電話番号',
            'post_code': '郵便番号',
            'address': '住所',
            'street_address': '番地以下',
            'bank_name': '銀行名',
            'branch_number': '支店番号',
            'bank_account_number': '口座番号',
        }

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

class EditProfileForm(forms.ModelForm):
    birthdate = forms.DateField(
        widget=forms.SelectDateWidget(years=[x for x in range(1900, 2024)]),
        label='生年月日'
    )
    
    class Meta:
        model = User
        fields = [
            'last_name', 'first_name', 'email', 'birthdate', 
            'telephone_number', 'post_code', 'address', 'street_address',
            'bank_name', 'branch_number', 'bank_account_number'
        ]
        labels = {
            'last_name': '名字',
            'first_name': '名前',
            'email': 'メールアドレス',
            'telephone_number': '電話番号',
            'post_code': '郵便番号',
            'address': '住所',
            'street_address': '番地以下',
            'bank_name': '銀行名',
            'branch_number': '支店番号',
            'bank_account_number': '口座番号',
        }
