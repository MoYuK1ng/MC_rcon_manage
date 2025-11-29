"""
URL Configuration for servers app
"""

from django.urls import path
from servers.views import DashboardView, PlayerListView, WhitelistAddView

from servers.views_lang import set_language

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('server/<int:server_id>/players/', PlayerListView.as_view(), name='player_list'),
    path('server/<int:server_id>/whitelist/', WhitelistAddView.as_view(), name='whitelist_add'),
    path('set-language/', set_language, name='set_language'),
]
