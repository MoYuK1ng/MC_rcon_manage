"""
Custom admin views for MC RCON Manager
"""

from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.db.models import Count


def admin_required(view_func):
    """Decorator to require admin/superuser access"""
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@admin_required
def ungrouped_users_view(request):
    """
    Display users who are not in any groups and allow quick group assignment.
    
    This view helps administrators quickly identify and assign permissions to
    users who have registered but haven't been given server access yet.
    """
    # Get all non-superuser users without any groups
    ungrouped_users = User.objects.filter(
        is_superuser=False,
        groups__isnull=True
    ).annotate(
        whitelist_count=Count('whitelistrequest')
    ).order_by('-date_joined')
    
    # Get all available groups for assignment
    available_groups = Group.objects.exclude(name__contains=" | ").order_by('name')
    
    # Handle group assignment POST request
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_ids = request.POST.getlist('groups')
        
        if user_id and group_ids:
            try:
                user = User.objects.get(id=user_id)
                groups = Group.objects.filter(id__in=group_ids)
                
                # Add user to selected groups
                user.groups.add(*groups)
                
                group_names = ', '.join([g.name for g in groups])
                messages.success(
                    request,
                    _(f'Successfully added user "{user.username}" to groups: {group_names}')
                )
                
                return redirect('admin:ungrouped_users')
            except User.DoesNotExist:
                messages.error(request, _('User not found'))
            except Exception as e:
                messages.error(request, _(f'Error assigning groups: {str(e)}'))
    
    context = {
        'title': _('Ungrouped Users / 未分组用户'),
        'ungrouped_users': ungrouped_users,
        'available_groups': available_groups,
        'user_count': ungrouped_users.count(),
        'opts': User._meta,  # For breadcrumbs
        'has_view_permission': True,
    }
    
    return render(request, 'admin/servers/ungrouped_users.html', context)
