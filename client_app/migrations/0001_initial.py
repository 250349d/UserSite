# Generated by Django 5.1.4 on 2025-01-20 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=150, verbose_name='商品名')),
                ('price', models.IntegerField(verbose_name='単価')),
                ('quantity', models.IntegerField(verbose_name='個数')),
                ('notes', models.CharField(blank=True, max_length=150, verbose_name='備考')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='申請時間')),
                ('price', models.IntegerField(verbose_name='申請金額')),
                ('status', models.CharField(default='0', help_text='0: 未承認, 1: 承認, 2: 非承認', max_length=1, verbose_name='申請ステータス')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, verbose_name='依頼件名')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='注文した時間')),
                ('limit_of_time', models.DateTimeField(verbose_name='配達期限時間')),
                ('status', models.CharField(default='0', help_text='0: 注文済み, 1: 配達中, 2: 承認待ち, 3: 再申請待ち, 4: 配達完了', max_length=1, verbose_name='配達ステータス')),
                ('delivery_completion_time', models.DateTimeField(blank=True, null=True, verbose_name='配達完了時間')),
                ('shop_name', models.CharField(max_length=150, verbose_name='店舗名')),
                ('shop_post_code', models.CharField(max_length=15, verbose_name='店舗の郵便番号')),
                ('shop_address', models.CharField(help_text='高知県香美市土佐山田町に続く住所', max_length=150, verbose_name='店舗の住所')),
                ('shop_street_address', models.CharField(max_length=150, verbose_name='店舗の番地')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.IntegerField(blank=True, null=True, verbose_name='商品合計金額')),
                ('courier_reward_amount', models.IntegerField(blank=True, null=True, verbose_name='給料')),
                ('delivery_fee', models.IntegerField(blank=True, null=True, verbose_name='配達手数料')),
                ('payment_fee_date', models.DateTimeField(blank=True, null=True, verbose_name='サービス代金支払い日付')),
                ('courier_item_payment_date', models.DateTimeField(blank=True, null=True, verbose_name='商品代金支払い日付')),
                ('courier_reward_date', models.DateTimeField(blank=True, null=True, verbose_name='報酬支払日付')),
                ('pay_courier_reward', models.BooleanField(blank=True, default=False, null=True)),
                ('pay_courier_item', models.BooleanField(blank=True, default=False, null=True)),
                ('pay_fee', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
    ]
