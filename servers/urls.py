"""
URL Configuration for servers app
"""

from django.urls import path
from servers.views import DashboardView, PlayerListView, WhitelistAddView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/zh/', DashboardView.as_view(), {'lang': 'zh'}, name='dashboard_zh'),
    path('server/<int:server_id>/players/', PlayerListView.as_view(), name='player_list'),
    path('server/<int:server_id>/whitelist/', WhitelistAddView.as_view(), name='whitelist_add'),
]
