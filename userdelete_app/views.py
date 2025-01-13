from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse

CustomUser = get_user_model()

@login_required
def delete_view(request):
    user = request.user
    user = get_object_or_404(CustomUser, id=user.id) # 対象ユーザの抽出
    logout(request)
    user.delete()
    return redirect(to='/homepage/')
