import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger('django')

CustomUser = get_user_model()

def get_sentinel_user():
	return CustomUser.objects.get_or_create(
		first_name = "None",
		last_name = "None",
		birthdate = '0000-00-00',
		post_code = "None",
		address = "None",
		street_address = "None",
		email = "none@example.com",
		telephone_number = "None"
	)[0]

# Create your models here.
# Task model
class Task(models.Model):
	client = models.ForeignKey(
		CustomUser,
		on_delete=models.SET(get_sentinel_user),
		related_name='client',
		verbose_name="クライアント",
	)
	worker = models.ForeignKey(
		CustomUser,
		on_delete=models.SET(get_sentinel_user),
		related_name='worker',
		null=True,
		blank=True,
		verbose_name="配達員",
	)
	title = models.CharField(
		max_length=60,
		verbose_name="依頼件名",
	)
	created_at = models.DateTimeField(
		auto_now_add=True,
		verbose_name="注文した時間",
	)
	limit_of_time = models.DateTimeField(
		verbose_name="配達期限時間",
	)
	status = models.CharField(
		max_length=1,
		default="0",
		verbose_name="配達ステータス",
		help_text="0: 注文済み, 1: 配達中, 2: 承認待ち, 3: 再申請待ち, 4: 配達完了",
	)

	delivery_completion_time = models.DateTimeField(
		blank=True,
		null=True,
		verbose_name="配達完了時間",
	)
	shop_name = models.CharField(
		max_length=150,
		verbose_name="店舗名",
	)
	shop_post_code = models.CharField(
		max_length=15,
		verbose_name="店舗の郵便番号",
	)
	shop_address = models.CharField(
		max_length=150,
		verbose_name="店舗の住所",
		help_text="高知県香美市土佐山田町に続く住所"
	)
	shop_street_address = models.CharField(
		max_length=150,
		verbose_name="店舗の番地",
	)

	def clean(self):
		super().clean() # 本来のclean()を実行

		limit_of_time = self.limit_of_time

		# 配達期限時間が設定されているか確認
		if limit_of_time:
			# タイムゾーンが設定されていない場合は設定する
			if limit_of_time.tzinfo is None:
				limit_of_time = timezone.make_aware(limit_of_time)

			# 配達期限時間が現在時刻より後の時間を設定しているか確認
			if limit_of_time <= timezone.now():
				raise ValidationError("配達期限時間は現在時刻より後の時間を設定してください。")
		else:
			raise ValidationError("配達期限時間を設定してください。")

		self.limit_of_time = limit_of_time

	def __str__(self):
		return f"Task {self.id} - Title: {self.title}"

# Transaction model
class Transaction(models.Model):
	task = models.OneToOneField(
		Task,  # 対応するTaskモデルのクラス名
		on_delete=models.CASCADE,  # Taskが削除されたときに対応するTransactionも削除される
		related_name='transaction',  # Taskモデルから関連するTransactionsをアクセスするための名前
		verbose_name="関連するタスク"
	)
	total_cost = models.IntegerField(
		blank=True,
		null=True,
		verbose_name="商品合計金額"
	)
	courier_reward_amount = models.IntegerField(
		blank=True,
		null=True,
		verbose_name="給料"
	)
	delivery_fee = models.IntegerField(
		blank=True,
		null=True,
		verbose_name="配達手数料"
	)
	payment_fee_date = models.DateTimeField(
		blank=True,
		null=True,
		verbose_name="サービス代金支払い日付"
	)
	courier_item_payment_date = models.DateTimeField(
		blank=True,
		null=True,
		verbose_name="商品代金支払い日付"
	)
	courier_reward_date = models.DateTimeField(
		blank=True,
		null=True,
		verbose_name="報酬支払日付"
	)
	pay_courier_reward = models.BooleanField(
		blank=True,
		null=True,
		default=False,
	)
	pay_courier_item = models.BooleanField(
		blank=True,
		null=True,
		default=False,
	)
	pay_fee = models.BooleanField(
		blank=True,
		null=True,
		default=False,
	)

	def __str__(self):
		return f"Transaction {self.task} - Total Cost: {self.total_cost}"

# Order model
class Order(models.Model):
	task = models.ForeignKey(
		Task,
		on_delete=models.CASCADE,
		related_name="order",
		verbose_name="注文"
	)
	product_name = models.CharField(
		max_length=150,
		verbose_name="商品名"
	)
	price = models.IntegerField(
		verbose_name="単価"
	)
	quantity = models.IntegerField(
		verbose_name="個数"
	)
	notes = models.CharField(
		max_length=150,
		blank=True,
		verbose_name="備考"
	)

	def __str__(self):
		return f"Order {self.id} - Product: {self.product_name}"

class Request(models.Model):
	task = models.ForeignKey(
		Task,
		on_delete=models.CASCADE,
		related_name="request",
		verbose_name="申請"
	)
	time = models.DateTimeField(
		auto_now_add=True,
		verbose_name="申請時間"
	)
	price = models.IntegerField(
		verbose_name="申請金額"
	)
	status = models.CharField(
		max_length=1,
		default="0",
		verbose_name="申請ステータス",
		help_text="0: 未承認, 1: 承認, 2: 非承認"
	)
