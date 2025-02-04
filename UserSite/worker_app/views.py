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
        worker=request.user,
        status__in=['1', '3']  # 配達中または再申請のタスク
    )

    # 依頼者の住所を取得
    delivery_address = f"{task.client.post_code} {task.client.address} {task.client.street_address}"

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 既存の完了申請がある場合は削除
                Request.objects.filter(task=task, status='2').delete()

                # 新しい完了申請を作成
                Request.objects.create(
                    task=task,
                    time=timezone.now(),
                    price=task.transaction.total_cost,
                    status='2'  # 承認待ち
                )

                # タスクのステータスを更新
                task.status = '2'  # 承認待ち
                task.delivery_completion_time = timezone.now()
                task.save()

                messages.success(request, '完了申請が送信されました。承認をお待ちください。')
                return redirect('worker_app:accepted_requests')
        except Exception as e:
            print(f"Error submitting completion: {e}")
            messages.error(request, '完了申請中にエラーが発生しました。')
            return redirect('worker_app:accepted_requests')

    return render(request, 'worker_app/submit_cost.html', {
        'task': task,
        'delivery_address': delivery_address
    })

@login_required
def cancel_request_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status == '1' and task.worker == request.user: # 確認
        if request.method == 'POST':
            task.status = 'C'  # Canceled
            task.worker = None  # 作業者をクリア
            task.save()
            return redirect('worker_app:mypage')  # マイページに戻る
    return render(request, 'worker_app/cancel_request.html', {'task': task})

@login_required
def approve_cost_view(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        client=request.user,
        status='2'  # 承認待ちのタスクのみ
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 最新の完了申請を取得
                completion_request = Request.objects.filter(
                    task=task, 
                    status='2'  # 承認待ち
                ).latest('time')
                
                # 申請を承認済みに更新
                completion_request.status = '1'  # 承認済み
                completion_request.save()

                # タスクのステータスを更新
                task.status = '4'  # 配達完了
                task.save()

                # トランザクションに報酬を設定
                transaction_obj = task.transaction
                transaction_obj.courier_reward_amount = int(completion_request.price * 0.8)  # 80%を報酬に
                transaction_obj.save()

                messages.success(request, '完了申請を承認しました。')
                return redirect('requester_home')
        except Request.DoesNotExist:
            messages.error(request, '承認可能な完了申請が見つかりませんでした。')
        except Exception as e:
            print(f"Error approving completion: {e}")
            messages.error(request, '承認中にエラーが発生しました。')

    # 完了申請の詳細を取得して表示
    try:
        completion_request = Request.objects.get(task=task, status='2')
        return render(request, 'worker_app/approve_cost.html', {
            'task': task,
            'completion_request': completion_request
        })
    except Request.DoesNotExist:
        messages.error(request, '承認可能な完了申請が見つかりませんでした。')
        return redirect('requester_home')

@login_required
def accepted_requests_view(request):
    """
    受注済みの依頼を確認するビュー（一覧）
    """
    now = timezone.now()
    tasks = Task.objects.select_related('transaction').prefetch_related('order').filter(
        worker=request.user,
        status__in=['1', '2', '3']  # Accepted, Waiting for Approval, Re-application
    ).order_by('limit_of_time')
    
    # 各タスクの期限状態を確認
    for task in tasks:
        # 最新の申請情報を取得
        try:
            latest_request = Request.objects.filter(task=task).latest('time')
            task.latest_request_status = latest_request.status
        except Request.DoesNotExist:
            task.latest_request_status = None

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
