from django.db import models
from client_app.models import Task

# Chat model
class Chat(models.Model):
	task = models.ForeignKey(
		Task,
		on_delete=models.CASCADE,
		related_name='chat',
		verbose_name="チャット",
		editable=False
	)
	sender_group = models.CharField(
		max_length=1,
		verbose_name="送信者の属性",
		help_text="0: 注文者, 1: 配達員",
		editable=False
	)
	send_time = models.DateTimeField(
		auto_now_add=True,
		verbose_name="メッセージ送信時間",
		editable=False
	)
	text = models.CharField(
		max_length=150,
		verbose_name="メッセージ文"
	)
	read_flag = models.BooleanField(
		default=False
	)

	def __str__(self):
		return f"Chat {self.id} - Task: {self.task}"
