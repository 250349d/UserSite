from django.shortcuts import render, redirect, get_object_or_404
from .forms import CpassForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.http import HttpResponse

@login_required
def passchange_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(user = request.user, data = request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect(to='/client_app/mypage/')
        else:
            form = PasswordChangeForm(user = request.user)
        param = {
            'form': form
        }
        return render(request, 'passchange_app/cpass.html' ,param)
            
    else:
        return redirect(to='/client_app/mypage/')
