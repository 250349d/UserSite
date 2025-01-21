import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

def get_all_objects():
    now = datetime.date.today()
    return Notification.objects.filter(
        limit_of_time__gt=now
    ).order_by('-created_at')

def get_filtered_objects_id(notification_id):
    try:
        return Notification.objects.filter(id=notification_id)
    except (ValueError, TypeError):
        print('TypeError')
        return None

@login_required
def list_view(request):
    objects = get_all_objects()
    params = {
        'objects': objects
    }
    return render(request, 'notification_app/list.html', params)

@login_required
def detail_view(request, notification_id):
    objects = get_filtered_objects_id(notification_id)
    if objects is None or not objects.exists():
        return redirect(to='/notfound/')
    params = {
        'objects': objects
    }
    return render(request, 'notification_app/detail.html', params)
