"""
Views for MC RCON Manager
Handles dashboard, player lists, and whitelist management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.core.exceptions import ValidationError
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login

from servers.models import Server, WhitelistRequest, Announcement
from servers.services.rcon_manager import RconHandler
from servers.decorators import user_has_server_access
from servers.forms import UserRegistrationForm


class CustomLoginView(LoginView):
    """
    Custom login view to handle template switching for Chinese language.
    """
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        """Handle GET requests: render the login form."""
        lang = request.COOKIES.get('user_lang', 'en')
        if lang == 'zh-hans':
            self.template_name = 'registration/login_zh.html'
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST requests: authenticate user."""
        lang = request.COOKIES.get('user_lang', 'en')
        if lang == 'zh-hans':
            self.template_name = 'registration/login_zh.html'
        
        return super().post(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """
    Main dashboard view showing servers accessible to the user.
    """
    template_name = 'servers/dashboard.html'
    
    def get(self, request):
        """Display dashboard with accessible servers."""
        if request.user.is_superuser:
            servers = Server.objects.all()
        else:
            servers = Server.objects.filter(groups__in=request.user.groups.all()).distinct()
        
        announcements = Announcement.objects.filter(is_active=True)
        
        context = {
            'servers': servers,
            'announcements': announcements,
        }
        
        lang = request.COOKIES.get('user_lang', 'en')
        template = 'servers/dashboard_zh.html' if lang == 'zh-hans' else self.template_name
        return render(request, template, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_has_server_access, name='dispatch')
class PlayerListView(View):
    """HTMX endpoint for fetching online players from a server."""
    template_name = 'servers/partials/player_list.html'
    
    def get(self, request, server_id):
        server = get_object_or_404(Server, id=server_id)
        handler = RconHandler(server)
        result = handler.get_players()
        
        context = {
            'server': server,
            'success': result['success'],
            'players': result.get('players', []),
            'message': result['message'],
        }
        
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_has_server_access, name='dispatch')
class WhitelistAddView(View):
    """Handle whitelist addition requests."""
    
    def post(self, request, server_id):
        server = get_object_or_404(Server, id=server_id)
        minecraft_username = request.POST.get('minecraft_username', '').strip()
        
        if not minecraft_username:
            messages.error(request, _('Please enter a Minecraft username.'))
            return redirect('dashboard')
        
        if WhitelistRequest.objects.filter(server=server, minecraft_username=minecraft_username).exists():
            messages.warning(request, _('This username is already on the whitelist or has a pending request.'))
            return redirect('dashboard')

        whitelist_request = WhitelistRequest(user=request.user, server=server, minecraft_username=minecraft_username)
        try:
            whitelist_request.full_clean()
        except ValidationError as e:
            for error_list in e.message_dict.values():
                for error in error_list:
                    messages.error(request, error)
            return redirect('dashboard')
        
        whitelist_request.save()
        
        handler = RconHandler(server)
        result = handler.add_whitelist(minecraft_username)
        
        if result['success']:
            whitelist_request.status = WhitelistRequest.Status.PROCESSED
            messages.success(request, _('Successfully added {username} to {server} whitelist.').format(username=minecraft_username, server=server.name))
        else:
            whitelist_request.status = WhitelistRequest.Status.FAILED
            messages.error(request, _('Failed to add {username} to whitelist: {error}').format(username=minecraft_username, error=result['message']))

        whitelist_request.response_log = result['message']
        whitelist_request.save()
        
        return redirect('dashboard')


class RegisterView(View):
    """User registration view with captcha verification."""
    template_name = 'registration/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = UserRegistrationForm()
        context = {'form': form}
        lang = request.COOKIES.get('user_lang', 'en')
        template = 'registration/register_zh.html' if lang == 'zh-hans' else self.template_name
        return render(request, template, context)
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
            
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, _('Registration successful! Welcome.'))
            return redirect('dashboard')
        
        context = {'form': form}
        lang = request.COOKIES.get('user_lang', 'en')
        template = 'registration/register_zh.html' if lang == 'zh-hans' else self.template_name
        return render(request, template, context)


class MyWhitelistView(View):
    """View for users to see their whitelist request history."""
    template_name = 'servers/my_whitelist.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        whitelist_requests = WhitelistRequest.objects.filter(user=request.user).select_related('server').order_by('-created_at')
        context = {'whitelist_requests': whitelist_requests}
        lang = request.COOKIES.get('user_lang', 'en')
        template = 'servers/my_whitelist_zh.html' if lang == 'zh-hans' else self.template_name
        return render(request, template, context)