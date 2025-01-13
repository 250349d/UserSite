from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Task, Transaction, Order, Request

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'last_name', 'first_name', 'telephone_number', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'last_name', 'first_name', 'telephone_number')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'last_name', 'first_name', 'birthdate', 'telephone_number',
            'post_code', 'address', 'street_address'
        )}),
        (_('Bank info'), {'fields': (
            'bank_name', 'branch_number', 'bank_account_number'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'worker', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'client__email', 'worker__email')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('task', 'total_cost', 'courier_reward_amount', 'delivery_fee')
    search_fields = ('task__title',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'task', 'price', 'quantity')
    search_fields = ('product_name', 'task__title')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('task', 'time', 'price', 'status')
    list_filter = ('status',)
    search_fields = ('task__title',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Request, RequestAdmin)
