import datetime
from django.shortcuts import render, redirect
from django.db import connections
from collections import namedtuple
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple("object", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def get_all_objects():
    now = datetime.date.today()
    print(now)
    with connections["manager_data"].cursor() as cursor:
        cursor.execute("SELECT * FROM notification_app_notification WHERE limit_of_time > date %s ORDER BY created_at DESC", [now])
        results = namedtuplefetchall(cursor)

    return results

def get_filtered_objects_id(expression):
    with connections["manager_data"].cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM notification_app_notification WHERE id=%s", str(expression))
            results = namedtuplefetchall(cursor)
        except TypeError:
            print('TypeError')
            results = None

    return results

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
    if objects == None:
        return redirect(to='/notfound/')
    params = {
        'objects': objects
    }
    return render(request, 'notification_app/detail.html', params)
