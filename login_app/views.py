from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm
from django.contrib.auth import login, logout

def login_view(request):

    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == 'None':
                    return redirect(to='/client/mypage/')
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

    return redirect('home_app:homepage')
