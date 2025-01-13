from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name = 'client_app'
urlpatterns = [
	# 注文機能
	path('create-order/', views.create_order, name='create-order'),

	# 注文確認機能
	path('check-order/', views.check_order, name='check-order'),
	path('check-order/detail/<int:task_id>/', views.check_order_detail, name='check-order-detail'),

	path('check-order/cancel/<int:task_id>/', views.cancel_order, name='cancel-order'),

	path('check-order/confirm/<int:task_id>/', views.confirm_request, name='confirm-request'),
	path('check-order/accept/', views.accept_request, name='accept-request'),
	path('check-order/reject/', views.reject_request, name='reject-request'),

	path('check-order/chat/', include('chat_app.urls')),

	# 完了済み依頼確認機能
	path('check-completed-order/', views.check_completed_order, name='check-completed-order'),
	path('check-completed-order/detail/<int:task_id>/', views.check_order_detail, name='check-completed-order-detail'),

	# 支払い機能
	path('check-payment/', views.check_payment, name='check-payment'),
	path('check-payment/detail/<int:task_id>/', views.check_order_detail, name='check-payment-detail'),
	path('check-payment/payment/<int:task_id>/', views.payment, name='payment'),
]