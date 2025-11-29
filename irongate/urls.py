"""
URL configuration for irongate project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('', include('servers.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
]