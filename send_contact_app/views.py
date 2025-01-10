from django.shortcuts import render, redirect
from .forms import ContactForm
from django.utils import timezone
from .models import CustomUser, Contact
from django.contrib.auth.decorators import login_required

@login_required
def send_contact_view(request):
    if request.method == 'GET':#GETメソッドの場合
        form = ContactForm()
        return render(request, 'send_contact_app/send_contact.html', {'form': form})#send_contact.htmlにfromを渡して表示
    elif request.method == 'POST':#POSTメソッドの場合
        form = ContactForm(request.POST)#POSTされたデータを取得
        if form.is_valid():
            try:
                contact = form.save(commit=False)
                user = request.user #認証したユーザを取得、ほんとはこっちを使う  
                contact.user = user
                contact.created_at = timezone.now()
                contact.save()
                return redirect('/client/mypage/')
            except Exception as e:
                return render(request, 'send_contact_app/send_contact.html', {'form': form, 'error': str(e)})
        else:
            return render(request, 'send_contact_app/send_contact.html', {'form': form, 'errors': form.errors})