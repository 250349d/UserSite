from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name = 'worker_app'
urlpatterns = [
    path('mypage/', views.mypage_view, name='mypage'), # マイページを表示

    path('receive/', views.receive_request_view, name='receive_request'), # 依頼受注（一覧）
    path('confirm_request/<int:pk>/', views.confirm_request_view, name='confirm_request'), # 依頼受注（詳細）

    path('accepted/', views.accepted_requests_view, name='accepted_requests'), # 受注済みの依頼を確認する（一覧）
    path('cancel_request/<int:pk>/', views.cancel_request_view, name='cancel_request'), # 依頼キャンセル
    path('submit_cost/<int:pk>/', views.submit_cost_view, name='submit_cost'), # 金額申請

    path('completed-request/', views.completed_requests_view, name='completed_requests'), # 完了依頼の確認（一覧）

    path('rewards/', views.reward_check_view, name='reward_check'), # 報酬確認

#    path('approve_cost/<int:pk>/', views.approve_cost_view, name='approve_cost'),
#    path('requester/', views.requester_home_view, name='requester_home'),
]
