from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import SignupForm, LoginForm, EditProfileForm
from django.contrib.auth import get_user_model

User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user')
    else:
        form = SignupForm()
    return render(request, 'edit_user_information_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user')
    else:
        form = LoginForm()
    return render(request, 'edit_user_information_app/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_view(request):
    return render(request, 'edit_user_information_app/user.html')

@login_required
def edit_view(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'edit_user_information_app/edit.html', {'form': form})
