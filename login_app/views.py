from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, LoginForm, CpassForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import HttpResponse

User = get_user_model()

def signup_view(request):
    #User.objects.delete(id=1)
    #print(User.objects.all())
    #return redirect(to='/login_app/login/')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='/login_app/login/')

    else:
        form = SignupForm()
    
    param = {
        'form': form
    }

    return render(request, 'login_app/signup.html', param)

def login_view(request):

    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == 'None':
                    return redirect(to='/login_app/user/')
                else:
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get('next')

    param = {
        'form': form,
        'next': next
    }

    return render(request, 'login_app/login.html', param)

def logout_view(request):
    logout(request)

    return render(request, 'login_app/logout.html')



@login_required
def password_change_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(user = request.user, data = request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect(to='/login_app/user/')
        else:
            form = PasswordChangeForm(user = request.user)
        param = {
            'form': form
        }
        return render(request, 'login_app/cpass.html' ,param)
            
    else:
        # return HttpResponseRedirect('login_app/login')
        return redirect(to='/login_app/login/')


@login_required
def user_view(request):
    user = request.user

    params = {
        'user': user
    }

    return render(request, 'login_app/user.html', params)

@login_required
def other_view(request):
    users = User.objects.exclude(username=request.user.username)

    params = {
        'users': users
    }

    return render(request, 'login_app/other.html', params)

@login_required
def delete_view(request):
    user = request.user
    User = get_user_model()
    user = User.objects.get(id=user.id) # 対象ユーザの抽出
    user.delete()
    return render(request, 'login_app/logout.html')

def password_reset_view(request):
    #if request.user.is_authenticated:
    if request.method == "POST":
        data=request.POST
        print(data.get("email"))
        user = get_object_or_404(User, email=data.get("email"))
        new_password = get_random_string(length=20)
        user.set_password(new_password)
        user.save()
        print(new_password)
        return redirect(to="/login_app/login/")
        # return HttpResponse(new_password)
        # #form = Form(user = request.user, data = request.POST)
        # if form.is_valid():
        #         form.save()
        #         update_session_auth_hash(request, form.user)
        #         return redirect(to='/login_app/user/')
        # else:
        #     form = PasswordChangeForm(user = request.user)
        # param = {
        #     'form': form
        # }
        # return render(request, 'login_app/cpass.html' ,param)
            
    else:
        # return HttpResponseRedirect('login_app/login')
        return render(request, "login_app/password_reset_request.html")

# @login_required
# def password_reset_request_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         if not email:
#             return render(request, 'login_app/password_reset_request.html', {'error': 'メールアドレスを入力してください。'})

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return render(request, 'login_app/password_reset_request.html', {'error': 'このメールアドレスのユーザーは存在しません。'})

#         # ランダムな10桁のパスワードを生成
#         new_password = get_random_string(length=10)
#         user.set_password(new_password)
#         user.save()

#         # メール送信
#         subject = "パスワード再設定のお知らせ"
#         message = f"新しいパスワードは以下の通りです：\n\n{new_password}\n\nログイン後、パスワードを変更してください。"
#         from_email = settings.DEFAULT_FROM_EMAIL
#         recipient_list = [email]

#         send_mail(subject, message, from_email, recipient_list)

#         return redirect('password_reset_done')  # 再設定完了ページにリダイレクト

#     return render(request, 'login_app/password_reset_request.html')


# def password_reset_request_view(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         try:
#             user = User.objects.get(email=email)
#             request.session['reset_user_id'] = user.id  # ユーザー情報をセッションに保存
#             return redirect('password_generate')
#         except User.DoesNotExist:
#             return render(request, 'login_app/password_reset_request.html', {'error': 'メールアドレスが見つかりませんでした。'})

#     return render(request, 'login_app/password_reset_request.html')

# def password_generate_view(request):
#     user_id = request.session.get('reset_user_id')
#     if not user_id:
#         return redirect('password_reset_request')

#     user = User.objects.get(id=user_id)

#     # ランダムな10桁のパスワードを生成
#     new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

#     # パスワードをハッシュ化して保存
#     user.password = make_password(new_password)
#     user.save()

#     # 新しいパスワードをメールで送信
#     send_mail(
#         subject="【重要】パスワードリセットのお知らせ",
#         message=f"こんにちは {user.username} さん,\n\n新しいパスワードは以下の通りです:\n\n{new_password}\n\nログイン後、速やかにパスワードを変更してください。",
#         from_email=None,  # settings.DEFAULT_FROM_EMAIL を使用
#         recipient_list=[user.email],
#         fail_silently=False,
#     )

#     return render(request, 'login_app/password_reset_done.html')