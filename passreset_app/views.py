from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.http import HttpResponse

CustomUser = get_user_model()

def password_reset_view(request):
    if request.method == "POST":
        data=request.POST
        print(data.get("email"))
        user = get_object_or_404(CustomUser, email=data.get("email"))
        new_password = get_random_string(length=20)
        user.set_password(new_password)
        user.save()
        print(new_password)
        #sendmail()でメールを送信
        return redirect(to="/login_app/login/")
    else:
        return render(request, "passreset_app/password_reset_request.html")
