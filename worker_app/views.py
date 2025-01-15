from django.contrib.auth import login, authenticate, logout
from client_app.models import Task, Transaction, Order, Request
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

# 0: 注文済み, 1: 配達中, 2: 承認待ち, 3: 再申請待ち, 4: 配達完了

CustomUser = get_user_model()

@login_required
def mypage_view(request):
    return render(request, 'worker_app/mypage.html', {'user': request.user})

@login_required
def receive_request_view(request):
    """
    受注可能依頼を表示するビュー
    """
    # 現在時刻で期限切れの依頼を除外
    now = timezone.now()
    pending_tasks = Task.objects.filter(
        status='0',  # 注文済み
        worker=None, # 配達員が決まっていない
        limit_of_time__gt=now  # 配達期限が現在時刻より後のもののみ
    ).exclude(
        client=request.user
    ).order_by('limit_of_time')
    return render(request, 'worker_app/receive_request.html', {'tasks': pending_tasks})

@login_required
def confirm_request_view(request, pk):
    """
    依頼を受注するビュー
    """
    task = get_object_or_404(
        Task.objects.select_related('transaction'),
        pk=pk
    )
    if request.method == 'POST':
        if task.status == '0' and task.worker is None:
            """
            try:
                with transaction.atomic():
                    task.status = '1'  # Accepted
                    task.worker = request.user
                    task.save()
                    return redirect('accepted_requests')
            except Exception as e:
                print(f"Error accepting task: {e}")
                return HttpResponse("依頼の受注中にエラーが発生しました", status=500)
            """
            task.status = '1'  # Accepted
            task.worker = request.user
            task.save()
            return redirect('worker_app:accepted_requests')
        return HttpResponse("この依頼は既に受注されています", status=400)

    orders = Order.objects.filter(task=task)
    context = {
        'task': task,
        'orders': orders,
        'total_cost': task.transaction.total_cost if hasattr(task, 'transaction') else 0
    }
    return render(request, 'worker_app/confirm_request.html', context)

@login_required
def submit_cost_view(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        worker=request.user
    )

    if request.method == 'POST':
        try:
            with transaction.atomic():
                task.status = '1'  # Delivered
                task.delivery_completion_time = timezone.now()
                task.save()

                # 配達完了時の申請を作成
                Request.objects.create(
                    task=task,
                    time=timezone.now(),
                    price=task.transaction.total_cost,
                    status='2'  # Pending approval
                )
                return redirect('accepted_requests')
        except Exception as e:
            print(f"Error submitting completion: {e}")
            return HttpResponse("完了申請中にエラーが発生しました", status=500)

    return render(request, 'worker_app/submit_cost.html', {'task': task})

@login_required
def cancel_request_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status == '1' and task.worker == request.user.id: # 確認
        if request.method == 'POST':
            task.status = 'C'  # Canceled
            task.save()
            return redirect('requester_home')
    return render(request, 'worker_app/cancel_request.html', {'task': task})

@login_required
def approve_cost_view(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        client=request.user
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                completion_request = Request.objects.get(task=task, status='P')
                completion_request.status = '1'  # Approved
                completion_request.save()

                transaction_obj = task.transaction
                transaction_obj.courier_reward_amount = int(completion_request.price * 0.8)  # 80%を報酬に
                transaction_obj.save()

                return redirect('requester_home')
        except Exception as e:
            print(f"Error approving completion: {e}")
            return HttpResponse("承認中にエラーが発生しました", status=500)

    return render(request, 'worker_app/approve_cost.html', {'task': task})

@login_required
def accepted_requests_view(request):
    """
    受注済みの依頼を確認するビュー（一覧）
    """
    now = timezone.now()
    tasks = Task.objects.select_related('transaction').prefetch_related('order').filter(
        worker=request.user,
        status='1'  # Accepted
    ).order_by('limit_of_time')
    
    # 各タスクの期限状態を確認
    for task in tasks:
        if task.limit_of_time < now:
            task.is_overdue = True
        else:
            time_remaining = task.limit_of_time - now
            # 残り1時間以内の場合は警告
            task.is_urgent = time_remaining.total_seconds() <= 3600

    return render(request, 'worker_app/accepted_requests.html', {'tasks': tasks})

@login_required
def completed_requests_view(request):
    completed_tasks = Task.objects.filter(
        worker=request.user,
        status='4'  # Delivered
    ).exclude(
        status='C'  # Canceled
    ).order_by('-delivery_completion_time')
    
    return render(request, 'worker_app/completed_requests.html', {'tasks': completed_tasks})

@login_required
def reward_check_view(request):
    completed_tasks = Task.objects.filter(
        worker=request.user,
        status='4'  # Delivered
    ).exclude(
        status='C'  # Canceled
    )
    
    total_reward = sum(task.transaction.courier_reward_amount for task in completed_tasks if hasattr(task, 'transaction'))
    completed_count = completed_tasks.count()
    
    context = {
        'total_reward': total_reward,
        'completed_count': completed_count,
        'tasks': completed_tasks
    }
    return render(request, 'worker_app/reward_check.html', context)
