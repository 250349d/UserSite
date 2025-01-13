import queue
import json

from django.http import StreamingHttpResponse, JsonResponse ,HttpResponseRedirect
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Chat

message_receive_queue = queue.Queue()
last_received_message_id = None

def event_stream(request):
	if request.headers.get('Accept') == 'text/event-stream':
		# event-streamのアクセスのみ許可
		response = StreamingHttpResponse(streaming_content=stream_events())
		response['Content-Type'] = 'text/event-stream'
		response['Cache-Control'] = 'no-cache'
		return response
	else:
		# event-stream以外のアクセスはリダイレクト
		return HttpResponseRedirect(reverse('chat_app:chat'))

def stream_events():
	#　ユーザー情報
	user_role = '1' # TODO:ログイン情報から取得するように変更する

	# メッセージ情報のフォーマット
	def format_message(message):
		data = {
			'sender_group': message.sender_group,
			'send_time': message.send_time.isoformat(),
			'text': message.text,
		}
		# 自身が送信したメッセージの場合は既読フラグを返す
		if message.sender_group == user_role:
			data['read_flag'] = message.read_flag

		return data

	# 既読フラグの更新
	def update_read_flag(message):
		# チャット相手が送信したメッセージの場合はフラグを更新
		if message.sender_group != user_role: return

		# 未読のメッセージのみ更新
		if message.read_flag == False:
			message.read_flag = True
			message.save()

	# メッセージ情報を返す際の処理（受信済みのid更新、既読フラグの更新、メッセージ情報のフォーマット）
	def process_message(message):
		global last_received_message_id
		last_received_message_id = message.id
		update_read_flag(message)
		return f"data: {json.dumps(format_message(message))}\n\n"

	# chat/にアクセスした際に全てのメッセージを表示
	messages = Chat.objects.all().order_by('id')
	for message in messages:
		yield process_message(message)

	# Chatテーブルが追加、更新されたときにキューに追加
	@receiver(post_save, sender=Chat)
	def message_saved(sender, **kwargs):
		message_receive_queue.put(True)

	# Chatテーブルが削除されたときにキューに追加
	@receiver(post_delete, sender=Chat)
	def message_deleted(sender, **kwargs):
		message_receive_queue.put(True)

	while True:
		try:
			# DBが更新されるまで待機（10秒更新がないとタイムアウト）
			message = message_receive_queue.get(timeout=10)

			# DBが更新されたら最新のメッセージを取得
			messages = Chat.objects.filter(id__gt=last_received_message_id).order_by('id')
			for message in messages:
				yield process_message(message)
		except queue.Empty:
			# SSEの接続が切れないように定期的にコメント行を返す
			yield f": ping\n\n"

# メッセージ送信情報を受け取り、DBに保存
def send_message(request):
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			Chat.objects.create(
				sender_group = '0',
				text = data.get('message'),
			)
			return JsonResponse({'success': True})
		except:
			return JsonResponse({'success': False})
	else:
		return HttpResponseRedirect(reverse('chat_app:chat'))