from django.db import models
from client_app.models import Task

# Chat model
class Chat(models.Model):
	task = models.ForeignKey(
		Task,
		on_delete=models.CASCADE,
		related_name='chat',
		null=True, # !!一時的にnullを許可
		verbose_name="チャット"
	)
	sender_group = models.CharField(
		max_length=1,
		verbose_name="送信者の属性(0: 注文者, 1: 配達員)"
	)
	send_time = models.DateTimeField(
		auto_now_add=True,
		verbose_name="メッセージ送信時間"
	)
	text = models.CharField(
		max_length=150,
		verbose_name="メッセージ文"
	)
	read_flag = models.BooleanField(
		default=False
	)
