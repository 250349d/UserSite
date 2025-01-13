from django.contrib import admin

from .models import Task, Transaction, Order, Request

admin.site.register(Task)
admin.site.register(Transaction)
admin.site.register(Order)
admin.site.register(Request)
