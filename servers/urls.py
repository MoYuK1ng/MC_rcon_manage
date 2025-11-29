"""
URL Configuration for servers app
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from servers.views import (
    DashboardView, 
    PlayerListView, 
    WhitelistAddView,
    RegisterView,
    MyWhitelistView,
    CustomLoginView
)
from servers.views_lang import set_language

urlpatterns = [
    # Main app views
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('server/<int:server_id>/players/', PlayerListView.as_view(), name='player_list'),
    path('server/<int:server_id>/whitelist/', WhitelistAddView.as_view(), name='whitelist_add'),
    path('my-whitelist/', MyWhitelistView.as_view(), name='my_whitelist'),

    # Auth views
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Language switcher
    path('set-language/', set_language, name='set_language'),
]
