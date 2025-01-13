from django.contrib.auth import login, authenticate, logout
from .models import Task, Transaction, Order, Request
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})

@login_required
@csrf_exempt
def create_request(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        shop_name = request.POST.get('shop_name')
        limit_of_time = request.POST.get('limit_of_time')
        shop_address = request.POST.get('shop_address')
        shop_street_address = request.POST.get('shop_street_address')
        shop_post_code = request.POST.get('shop_post_code')
        
        # 入力値のバリデーション
        errors = []
        if not title:
            errors.append("依頼件名を入力してください")
        if not shop_name:
            errors.append("店舗名を入力してください")
        if not limit_of_time:
            errors.append("配達期限時間を入力してください")
        if not shop_address:
            errors.append("店舗の住所を入力してください")
        if not shop_street_address:
            errors.append("店舗の番地を入力してください")
        if not shop_post_code:
            errors.append("店舗の郵便番号を入力してください")
        
        # 商品情報のリスト
        orders = []
        total_cost = 0
        i = 0
        has_products = False
        
        while True:
            product_name = request.POST.get(f'product_name_{i}')
            if not product_name:
                break
                
            quantity_str = request.POST.get(f'quantity_{i}')
            price_str = request.POST.get(f'price_{i}')
            
            if not quantity_str or not price_str:
                errors.append(f"{product_name}の数量と価格を入力してください")
                i += 1
                continue
                
            try:
                quantity = int(quantity_str)
                price = int(price_str)
                if quantity <= 0:
                    errors.append(f"{product_name}の数量は1以上を入力してください")
                if price <= 0:
                    errors.append(f"{product_name}の価格は1以上を入力してください")
            except ValueError:
                errors.append(f"{product_name}の数量と価格は数値を入力してください")
                i += 1
                continue
                
            notes = request.POST.get(f'notes_{i}')
            subtotal = quantity * price
            total_cost += subtotal
            
            orders.append({
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
                'notes': notes
            })
            has_products = True
            i += 1
            
        if not has_products:
            errors.append("商品情報を少なくとも1つ入力してください")

        if errors:
            return render(request, 'create_request.html', {
                'errors': errors,
                'form_data': request.POST  # 入力値を保持
            })

        try:
            with transaction.atomic():
                # タスクを作成
                task = Task.objects.create(
                    client=request.user,
                    title=title,
                    shop_name=shop_name,
                    limit_of_time=limit_of_time,
                    shop_address=shop_address,
                    shop_street_address=shop_street_address,
                    shop_post_code=shop_post_code,
                    status='P'  # Pending
                )

                # 商品情報を保存
                for order_data in orders:
                    Order.objects.create(
                        task=task,
                        **order_data
                    )

                # 取引情報を作成
                Transaction.objects.create(
                    task=task,
                    total_cost=total_cost,
                    delivery_fee=500  # 基本配達料金
                )

            messages.success(request, '依頼を作成しました')
            return redirect('requester_home')
        except Exception as e:
            print(f"Error creating request: {e}")
            messages.error(request, "依頼の作成中にエラーが発生しました")
            return render(request, 'create_request.html', {
                'errors': ["システムエラーが発生しました。もう一度お試しください。"],
                'form_data': request.POST
            })

    return render(request, 'create_request.html')

@login_required
def requester_home(request):
    # クライアントの依頼一覧を取得
    tasks = Task.objects.filter(
        client=request.user
    ).exclude(
        status='C'  # Canceled
    ).order_by('-created_at')
    return render(request, 'requester_home.html', {'tasks': tasks})

@login_required
def receive_request(request):
    # 現在時刻で期限切れの依頼を除外
    now = timezone.now()
    pending_tasks = Task.objects.filter(
        status='P',  # Pending
        worker=None,
        limit_of_time__gt=now  # 配達期限が現在時刻より後のもののみ
    ).exclude(
        client=request.user
    ).order_by('limit_of_time')
    return render(request, 'receive_request.html', {'tasks': pending_tasks})

@login_required
def confirm_request(request, pk):
    task = get_object_or_404(
        Task.objects.select_related('transaction'),
        pk=pk
    )
    
    if request.method == 'POST':
        if task.status == 'P' and task.worker is None:
            try:
                with transaction.atomic():
                    task.status = 'A'  # Accepted
                    task.worker = request.user
                    task.save()
                    return redirect('accepted_requests')
            except Exception as e:
                print(f"Error accepting task: {e}")
                return HttpResponse("依頼の受注中にエラーが発生しました", status=500)
        return HttpResponse("この依頼は既に受注されています", status=400)

    orders = Order.objects.filter(task=task)
    context = {
        'task': task,
        'orders': orders,
        'total_cost': task.transaction.total_cost if hasattr(task, 'transaction') else 0
    }
    return render(request, 'confirm_request.html', context)

@login_required
def submit_cost(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        worker=request.user
    )

    if request.method == 'POST':
        try:
            with transaction.atomic():
                task.status = 'D'  # Delivered
                task.delivery_completion_time = timezone.now()
                task.save()

                # 配達完了時の申請を作成
                Request.objects.create(
                    task=task,
                    time=timezone.now(),
                    price=task.transaction.total_cost,
                    status='P'  # Pending approval
                )
                return redirect('accepted_requests')
        except Exception as e:
            print(f"Error submitting completion: {e}")
            return HttpResponse("完了申請中にエラーが発生しました", status=500)

    return render(request, 'submit_cost.html', {'task': task})

@login_required
def cancel_request(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.status = 'C'  # Canceled
        task.save()
        return redirect('requester_home')
    return render(request, 'cancel_request.html', {'task': task})

@login_required
def approve_cost(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        client=request.user
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                completion_request = Request.objects.get(task=task, status='P')
                completion_request.status = 'A'  # Approved
                completion_request.save()

                transaction_obj = task.transaction
                transaction_obj.courier_reward_amount = int(completion_request.price * 0.8)  # 80%を報酬に
                transaction_obj.save()

                return redirect('requester_home')
        except Exception as e:
            print(f"Error approving completion: {e}")
            return HttpResponse("承認中にエラーが発生しました", status=500)

    return render(request, 'approve_cost.html', {'task': task})

@login_required
def accepted_requests(request):
    now = timezone.now()
    tasks = Task.objects.select_related('transaction').prefetch_related('orders').filter(
        worker=request.user,
        status='A'  # Accepted
    ).order_by('limit_of_time')
    
    # 各タスクの期限状態を確認
    for task in tasks:
        if task.limit_of_time < now:
            task.is_overdue = True
        else:
            time_remaining = task.limit_of_time - now
            # 残り1時間以内の場合は警告
            task.is_urgent = time_remaining.total_seconds() <= 3600
    
    return render(request, 'accepted_requests.html', {'tasks': tasks})

@login_required
def completed_requests_view(request):
    completed_tasks = Task.objects.filter(
        worker=request.user,
        status='D'  # Delivered
    ).exclude(
        status='C'  # Canceled
    ).order_by('-delivery_completion_time')
    
    return render(request, 'completed_requests.html', {'tasks': completed_tasks})

@login_required
def reward_check(request):
    completed_tasks = Task.objects.filter(
        worker=request.user,
        status='D'  # Delivered
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
    return render(request, 'reward_check.html', context)