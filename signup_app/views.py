from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm
from django.contrib.auth import login

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(to='/client/mypage/')

    else:
        form = SignupForm()
    
    param = {
        'form': form
    }

    return render(request, 'signup_app/signup.html', param)
