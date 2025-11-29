"""
Custom Decorators for MC RCON Manager
Provides access control decorators for views
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from servers.models import Server


def user_has_server_access(view_func):
    """
    Decorator to check if a user has access to a specific server.
    
    Verifies that the user belongs to at least one group that has access to the server.
    Superusers always have access.
    
    Usage:
        @user_has_server_access
        def my_view(request, server_id):
            ...
    
    Args:
        view_func: The view function to wrap
    
    Returns:
        Wrapped view function that checks server access
    
    Raises:
        HttpResponseForbidden: If user doesn't have access to the server
    """
    @wraps(view_func)
    def wrapper(request, server_id, *args, **kwargs):
        # Get the server or return 404
        server = get_object_or_404(Server, id=server_id)
        
        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, server_id, *args, **kwargs)
        
        # Check if user's groups intersect with server's groups
        user_groups = request.user.groups.all()
        server_groups = server.groups.all()
        
        # Check for intersection
        has_access = server_groups.filter(id__in=user_groups.values_list('id', flat=True)).exists()
        
        if not has_access:
            return HttpResponseForbidden(
                _('You do not have permission to access this server.')
            )
        
        return view_func(request, server_id, *args, **kwargs)
    
    return wrapper
