from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import EditProfileForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@login_required
def edit_view(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('client_app:mypage')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'edit_user_information_app/edit.html', {'form': form})
