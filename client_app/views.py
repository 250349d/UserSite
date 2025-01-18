import json
import math
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Task, Transaction, Order, Request

logger = logging.getLogger('django')

# 注文機能
@login_required
def create_order(request):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			data = json.loads(request.body)

			# 注文情報を取得
			title = data.get('title')
			limit_of_time = data.get('limit_of_time')
			shop_name = data.get('shop_name')
			shop_post_code = data.get('shop_post_code')
			shop_address = data.get('shop_address')
			shop_street_address = data.get('shop_street_address')

			task = Task(
				# 依頼情報
				client=request.user,
				worker=None,
				title=title,
				limit_of_time=limit_of_time,
				# 店舗情報
				shop_name=shop_name,
				shop_post_code=shop_post_code,
				shop_address=shop_address,
				shop_street_address=shop_street_address,
			)
			task.full_clean()
			task.save()

			# 注文内容の取得
			product_name_list = data.get('product_name_list')
			price_list = data.get('price_list')
			quantity_list = data.get('quantity_list')
			notes_list = data.get('notes_list')

			total_cost = 0 # 商品合計金額

			order_list = zip(product_name_list, price_list, quantity_list, notes_list)
			for product_name, price, quantity, notes in order_list:
				order = Order(
					task=task, # 上で作成したtaskに紐づける
					product_name=product_name,
					price=price,
					quantity=quantity,
					notes=notes,
				)
				order.full_clean()
				order.save()

				total_cost += int(price) * int(quantity) # 商品合計金額を計算

			# 取引情報を作成・更新
			Transaction.objects.create(task=task)
			summarize_financials(task, total_cost)

			is_success = True
		except ValidationError as e:
			error_message = "入力内容に誤り、または空欄があります"
			logger.error(e.message_dict)
		except Exception as e:
			logger.error(e)
		finally:
			if not is_success:
				# エラーが発生した場合の処理
				if task and task.pk is not None:
					task.delete() # 作成したtaskを削除

			return JsonResponse({'success': is_success, 'error_message': error_message})
	else:
		# 注文画面を表示
		return render(request, 'client_app/create_order.html')

# 注文確認機能
@login_required
def check_order(request):
	tasks = Task.objects.filter(
		client=request.user, # 注文者がログインユーザー
		transaction__payment_fee_date__isnull=True # 支払い済みでない
	)
	return render(request, 'client_app/check_order.html', {'tasks': tasks})

# 注文詳細確認機能
@login_required
def check_order_detail(request, task_id):
	task = get_object_or_404(Task, pk=task_id)
	# 注文者がログインユーザーでない場合はリダイレクト
	if task.client != request.user:
		return redirect('client_app:check-order')

	orders = Order.objects.filter(task=task)
	# 小計を計算
	for order in orders:
		order.subtotal = order.price * order.quantity
	return render(request, 'client_app/order_detail.html', {'task': task, 'orders': orders})

# 注文キャンセル機能
@login_required
def cancel_order(request, task_id):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			task = Task.objects.get(pk=task_id)
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			# キャンセル可能かチェック
			if task.status not in ['0']:
				error_message = "この注文は受注済みです"
				raise Exception(error_message)

			task.delete() # 注文を削除

			is_success = True
		except Exception as e:
			logger.error(e)
		finally:
			return JsonResponse({'success': is_success, 'error_message': error_message})
	else:
		return redirect('client_app:check-order')

# 申請確認機能
@login_required
def confirm_request(request, task_id):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			task = Task.objects.get(pk=task_id)
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			# 最新の申請情報を取得
			try:
				latest_request = Request.objects.filter(task=task).latest('time')
				latest_request_id = latest_request.id
				latest_request_price = latest_request.price
			except Request.DoesNotExist:
				latest_request = None
				latest_request_id = None
				latest_request_price = None

			# 未承認の申請情報がない
			if not latest_request or latest_request.status != '0':
				error_message = "未承認の申請情報がありません"
				raise Exception(error_message)

			is_success = True
		except Exception as e:
			logger.error(e)
		finally:
			return JsonResponse({
				'success': is_success,
				'request_id': latest_request_id,
				'request_price': latest_request_price,
				'error_message': error_message,
			})
	else:
		return redirect('client_app:check-order')

# 申請承認機能
@login_required
def accept_request(request):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			data = json.loads(request.body)

			request_id = data.get('request_id')
			request = Request.objects.get(pk=request_id)

			task = request.task
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			# 申請情報のステータスを承認に変更
			request.status = '1'
			request.save()

			# 申請金額による取引情報の更新
			summarize_financials(request.task, request.price)

			is_success = True
		except Exception as e:
			request.status = '0' # エラーが発生した場合は未承認に戻す
			request.save()

			logger.error(e)
		finally:
			return JsonResponse({'success': is_success, 'error_message': error_message})
	else:
		return redirect('client_app:check-order')

# 注文料金・配達員の給料などを商品合計金額をもとに計算
def summarize_financials(task, total_cost):
	try:
		order_fee_rate = 0.25 # 注文手数料率
		order_fee = total_cost * order_fee_rate # 注文手数料

		delivery_fee = 300 # 配達手数料

		total_fee = order_fee + delivery_fee # 基本合計手数料

		# オプション料金の計算
		if total_cost >= 2000:
			# 2000円以上の場合、1000円超過ごとに100円追加
			total_fee += (total_cost - 2000) // 1000 * 100

		# TODO: 時間帯はどのタイミングを取得するのか

		# 配達員の給料
		courier_reward_rate = 0.3 # 配達員報酬率
		courier_reward = math.ceil(total_fee * courier_reward_rate) # 端数は切り上げ

		# 取引情報の更新
		transaction = Transaction.objects.get(task=task)
		transaction.total_cost = total_cost
		transaction.courier_reward_amount = courier_reward
		transaction.delivery_fee = total_fee
		transaction.full_clean()
		transaction.save()
	except Exception as e:
		raise e

# 申請非承認機能
@login_required
def reject_request(request):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			data = json.loads(request.body)

			request_id = data.get('request_id')
			request = Request.objects.get(pk=request_id)

			task = request.task
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			# 申請情報のステータスを非承認に変更
			request.status = '2'
			request.full_clean()
			request.save()

			#非承認メールを送信
			send_mail(
				'【Flatosa】申請が非承認となりました',
				'あなたの申請が非承認となりました。詳細はアプリをご確認ください。',
				'from@example.com',
				['to@exxample.com'],
			)

			is_success = True
		except Exception as e:
			logger.error(e)
		finally:
			return JsonResponse({'success': is_success, 'error_message': error_message})
	else:
		return redirect('client_app:check-order')

# 完了済み依頼確認機能
@login_required
def check_completed_order(request):
	tasks = Task.objects.filter(
		client=request.user, # 注文者がログインユーザー
		transaction__payment_fee_date__isnull=False # 支払い済み
	)
	return render(request, 'client_app/check_completed_order.html', {'tasks': tasks})


# 支払い金額確認機能
@login_required
def check_payment(request):
	if request.method == 'POST':
		is_success = False
		error_message = "エラーが発生しました"
		try:
			data = json.loads(request.body)

			task_id = data.get('task_id')
			task = Task.objects.get(pk=task_id)
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			transaction = Transaction.objects.get(task=task)

			is_success = True
		except Exception as e:
			logger.error(e)
		finally:
			return JsonResponse({
				'success': is_success,
				'total_cost': transaction.total_cost,
				'product_cost': transaction.total_cost - transaction.delivery_fee,
				'delivery_fee': transaction.delivery_fee,
				'error_message': error_message
			})
	else:
		payment_tasks = Task.objects.filter(
			client=request.user, # 注文者がログインユーザー
			transaction__payment_fee_date__isnull=True, # 支払い済みでない
			status='4' # 注文ステータスが完了済み
		)
		return render(request, 'client_app/check_payment.html', {'tasks': payment_tasks})

# 支払い機能
@login_required
def payment(request, task_id):
	if request.method == 'POST':
		is_success = False
		error_message = "お支払い中に何らかの問題が起きました"
		try:
			data = json.loads(request.body)

			task_id = data.get('task_id')
			task = Task.objects.get(pk=task_id)
			# 注文者がログインユーザーでない場合はエラー処理
			if task.client != request.user:
				error_message = "注文者がログインユーザーではありません"
				raise Exception(error_message)

			name = data.get('name')
			card_number = data.get('card_number')
			cvc = data.get('cvc')
			expiry_date = data.get('expiry_date')

			# TODO: 疑似的な決済処理
			if not name or not card_number or not cvc or not expiry_date:
				error_message = "入力内容に誤り、または空欄があります"
				raise Exception(error_message)

			if len(card_number) != 16 or not card_number.isdigit():
				error_message = "カード番号が無効です"
				raise Exception(error_message)

			if len(cvc) != 3 or not cvc.isdigit():
				error_message = "CVCが無効です"
				raise Exception(error_message)

			try:
				expiry_month, expiry_year = map(int, expiry_date.split('/'))
			except Exception:
				error_message = "有効期限の入力形式が無効です"
				raise Exception(error_message)

			if expiry_month < 1 or expiry_month > 12:
				error_message = "有効期限の月が無効です"
				raise ValueError(error_message)
			current_year = timezone.now().year % 100 # 2025 -> 25
			current_month = timezone.now().month
			if expiry_year < current_year or (expiry_year == current_year and expiry_month < current_month):
				error_message = "有効期限が切れています"
				raise ValueError(error_message)

			# DBに支払い日時を保存
			transaction = Transaction.objects.get(task=task)
			transaction.payment_fee_date = timezone.now()
			transaction.full_clean()
			transaction.save()

			is_success = True
		except Exception as e:
			logger.error(e)
		finally:
			return JsonResponse({'success': is_success, 'error_message': error_message})
	else:
		# 支払い方法入力画面の表示
		task = get_object_or_404(Task, pk=task_id)
		# 注文者がログインユーザーでない場合はリダイレクト
		if task.client != request.user:
			return redirect('client_app:check-order')
		total_cost = task.transaction.total_cost or 0
		return render(request, 'client_app/payment.html', {'task_id': task_id, 'total_cost': total_cost})