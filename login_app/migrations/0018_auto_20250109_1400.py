# Generated by Django 3.2 on 2025-01-09 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0017_alter_customuser_town_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='名'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='姓'),
        ),
    ]
