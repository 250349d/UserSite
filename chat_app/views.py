import queue
import threading
import json
import logging

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.urls import reverse
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition

from .models import Chat
from client_app.models import Task

logger = logging.getLogger('django')

# チャット画面の表示
@login_required
def show_chat(request, task_id):
	task = get_object_or_404(Task, id=task_id)
	if request.user == task.client:
		# ログインユーザーが注文者の場合
		user_role = '0'
	elif request.user == task.worker:
		# ログインユーザーが配達員の場合
		user_role = '1'
	else:
		# ログインユーザーが注文者でも配達員でもない場合は404エラー
		return HttpResponse(status=404)

	return render(request, 'chat_app/chat.html', {
		'event_stream_url': reverse('chat_app:event-stream', args=(task_id,)),
		'update_message_url': reverse('chat_app:update-message'),
		'send_message_url': reverse('chat_app:send-message'),
		'task': task,
		'user_role': user_role,

	})

# チャット情報のストリーミング
@login_required
def event_stream(request, task_id):
	task = Task.objects.get(id=task_id)
	user_role = None
	if request.user == task.client:
		# ログインユーザーが注文者の場合
		user_role = '0'
	elif request.user == task.worker:
		# ログインユーザーが配達員の場合
		user_role = '1'
	else:
		# ログインユーザーが注文者でも配達員でもない場合はリダイレクト
		return redirect('chat_app:chat')

	if request.headers.get('Accept') == 'text/event-stream':
		# event-streamが指定された場合はストリーミングレスポンスを返す
		response = StreamingHttpResponse(
			streaming_content=stream_events(task, user_role, request)
		)
		response['Content-Type'] = 'text/event-stream'
		response['Cache-Control'] = 'no-cache'
		return response
	else:
		# event-stream以外の場合はリダイレクト
		return redirect('chat_app:chat')

# チャット情報の取得
def stream_events(task, user_role, request):
	# チャット情報のキューの初期化
	chat_queue = queue.Queue()

	# アクセス時に既存のチャットをキューに追加
	chats = Chat.objects.filter(task=task).order_by('id')
	for chat in chats:
		chat_queue.put({
			'chat': chat,
			'type': 'create', # 既存のチャットは新規作成として扱う
		})

	# Chatテーブルが作成、更新されたときにキューに追加
	@receiver(post_save, sender=Chat)
	def chat_saved(sender, **kwargs):
		chat = kwargs['instance']
		if chat.task == task:
			if kwargs['created']:
				chat_queue.put({
					'chat': chat,
					'type': 'create',
				})
			else:
				chat_queue.put({
					'chat': chat,
					'type': 'update',
				})

	@receiver(pre_delete, sender=Chat)
	def chat_deleted(sender, **kwargs):
		chat = kwargs['instance']
		if chat.task == task:
			chat_queue.put({
				'chat': chat,
				'type': 'delete',
		})

	# チャット情報のフォーマット
	def format_chat(chat):
		data = {
			'sender_group': chat.sender_group,
			'send_time': chat.send_time.isoformat(),
			'text': chat.text,
		}

		# 自身が送信したチャットの場合は既読情報を返す
		if chat.sender_group == user_role:
			data['read_flag'] = chat.read_flag

		# 同一Taskの中で何番目のチャットかを返す
		task_chats = Chat.objects.filter(task=task).order_by('id')
		chat_index = list(task_chats).index(chat) + 1 # 1-based index
		data['index'] = chat_index

		return data

	# チャット情報のストリーミング
	while True:
		queue_data = None
		try:
			# DBが更新されるまで待機（10秒更新がないとタイムアウト）
			queue_data = chat_queue.get(timeout=10)
		except queue.Empty:
			# タイムアウトしたら、SSEの接続が切れないようにコメント行を返す
			yield f"event: ping\n\n"
			continue

		chat = queue_data['chat']
		type = queue_data['type']

		data = None
		# チャットが作成か更新された場合はチャット情報を返す
		if type == 'create' or type == 'update':
			data = format_chat(chat)
			data['type'] = type
		# チャットが削除された場合はhtmlをすべて削除してチャット情報を再送信
		elif type == 'delete':
			# 全チャット情報をキューに追加
			chats = Chat.objects.filter(task=task).order_by('id')
			for chat in chats:
				chat_queue.put({
					'chat': chat,
					'type': 'create',
				})
			data['type'] = type

		# チャット情報を返す
		yield f"data: {json.dumps(data)}\n\n"

# チャット情報の更新
@login_required
def update_message(request):
	# 既読フラグの更新
	def update_read_flag(chat, user_role):
		# 自身が送信したチャットの場合は更新しない
		if chat.sender_group == user_role: return

		# 未読のチャットのみ更新
		if chat.read_flag == False:
			chat.read_flag = True
			chat.save()

	if request.method == "POST":
		try:
			data = json.loads(request.body)
			task_id = data.get('task_id')
			message_index = data.get('message_index')

			task = Task.objects.get(id=task_id)
			user_role = None
			if request.user == task.client:
				# ログインユーザーが注文者の場合
				user_role = '0'
			elif request.user == task.worker:
				# ログインユーザーが配達員の場合
				user_role = '1'
			else:
				# ログインユーザーが注文者でも配達員でもない場合はエラー処理
				raise Exception('ユーザーが注文者でも配達員でもありません')

			# チャット情報の取得
			chats = Chat.objects.filter(task=task).order_by('id')
			chat = chats[message_index - 1] # message_indexは1-based index

			# 既読フラグの更新
			update_read_flag(chat, user_role)

			return JsonResponse({'success': True})
		except Exception as e:
			logger.error(e)
			return JsonResponse({'success': False})
	else:
		return redirect('chat_app:chat')

# チャット送信情報を受け取り、DBに保存
@login_required
def send_message(request):
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			task_id = data.get('task_id')
			text = data.get('message')

			task = Task.objects.get(id=task_id)
			sender_group = None
			if request.user == task.client:
				# ログインユーザーが注文者の場合
				sender_group = '0'
			elif request.user == task.worker:
				# ログインユーザーが配達員の場合
				sender_group = '1'
			else:
				# ログインユーザーが注文者でも配達員でもない場合はエラー処理
				raise Exception('ユーザーが注文者でも配達員でもありません')

			Chat.objects.create(
				task = task,
				sender_group = sender_group,
				text = text,
			)
			return JsonResponse({'success': True})
		except Exception as e:
			logger.error(e)
			return JsonResponse({'success': False})
	else:
		return redirect('chat_app:chat')