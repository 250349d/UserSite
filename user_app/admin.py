from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
#from .models import CustomUser
from client_app.models import Task, Transaction, Request, Order
from send_contact_app.models import Contact
from chat_app.models import Chat

admin.site.register(Task)
admin.site.register(Transaction)
admin.site.register(Request)
admin.site.register(Order)
admin.site.register(Contact)
admin.site.register(Chat)
