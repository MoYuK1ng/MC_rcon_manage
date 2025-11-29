"""
URL Configuration for servers app
"""

from django.urls import path
from servers.views import (
    DashboardView, 
    PlayerListView, 
    WhitelistAddView,
    RegisterView,
    MyWhitelistView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('server/<int:server_id>/players/', PlayerListView.as_view(), name='player_list'),
    path('server/<int:server_id>/whitelist/', WhitelistAddView.as_view(), name='whitelist_add'),
    path('register/', RegisterView.as_view(), name='register'),
    path('my-whitelist/', MyWhitelistView.as_view(), name='my_whitelist'),
]
