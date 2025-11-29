"""
Views for IronGate RCON Portal
Handles dashboard, player lists, and whitelist management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.core.exceptions import ValidationError

from servers.models import Server, WhitelistRequest
from servers.services.rcon_manager import RconHandler
from servers.decorators import user_has_server_access
from django.http import HttpResponse


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """
    Main dashboard view showing servers accessible to the user.
    
    Displays all servers that the user has access to through their group memberships.
    """
    template_name = 'servers/dashboard.html'
    
    def get(self, request):
        """
        Display dashboard with accessible servers.
        
        Returns:
            Rendered dashboard template with server list
        """
        # Get servers accessible to user's groups
        if request.user.is_superuser:
            # Superusers see all servers
            servers = Server.objects.all()
        else:
            # Regular users see only servers linked to their groups
            servers = Server.objects.filter(
                groups__in=request.user.groups.all()
            ).distinct()
        
        context = {
            'servers': servers,
        }
        
        # Check language preference from cookie
        lang = request.COOKIES.get('user_lang', 'en')
        
        # Use Chinese template if lang=zh
        if lang == 'zh':
            return render(request, 'servers/dashboard_zh.html', context)
        
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_has_server_access, name='dispatch')
class PlayerListView(View):
    """
    HTMX endpoint for fetching online players from a server.
    
    Returns an HTML fragment that can be swapped into the page.
    """
    template_name = 'servers/partials/player_list.html'
    
    def get(self, request, server_id):
        """
        Get list of online players from server.
        
        Args:
            server_id: ID of the server to query
        
        Returns:
            Rendered HTML fragment with player list
        """
        server = get_object_or_404(Server, id=server_id)
        
        # Get players via RCON
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
    """
    Handle whitelist addition requests.
    
    Validates the Minecraft username and adds it to the server's whitelist via RCON.
    """
    
    def post(self, request, server_id):
        """
        Process whitelist addition request.
        
        Args:
            server_id: ID of the server to add whitelist to
        
        Returns:
            Redirect to dashboard with success/error message
        """
        server = get_object_or_404(Server, id=server_id)
        minecraft_username = request.POST.get('minecraft_username', '').strip()
        
        if not minecraft_username:
            messages.error(request, _('Please enter a Minecraft username.'))
            return redirect('dashboard')
        
        # Create whitelist request
        whitelist_request = WhitelistRequest(
            user=request.user,
            server=server,
            minecraft_username=minecraft_username
        )
        
        # Validate the username
        try:
            whitelist_request.full_clean()
        except ValidationError as e:
            error_messages = e.message_dict.get('minecraft_username', [])
            for error_msg in error_messages:
                messages.error(request, error_msg)
            return redirect('dashboard')
        
        # Save the request
        whitelist_request.save()
        
        # Execute RCON command
        handler = RconHandler(server)
        result = handler.add_whitelist(minecraft_username)
        
        # Update request status based on result
        if result['success']:
            whitelist_request.status = WhitelistRequest.Status.PROCESSED
            whitelist_request.response_log = result['message']
            whitelist_request.save()
            
            messages.success(
                request,
                _('Successfully added {username} to {server} whitelist.').format(
                    username=minecraft_username,
                    server=server.name
                )
            )
        else:
            whitelist_request.status = WhitelistRequest.Status.FAILED
            whitelist_request.response_log = result['message']
            whitelist_request.save()
            
            messages.error(
                request,
                _('Failed to add {username} to whitelist: {error}').format(
                    username=minecraft_username,
                    error=result['message']
                )
            )
        
        return redirect('dashboard')
