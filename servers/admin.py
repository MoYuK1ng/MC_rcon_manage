"""
Django Admin Configuration for IronGate
Registers Server and WhitelistRequest models with custom admin interfaces
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from servers.models import Server, WhitelistRequest


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    """Admin interface for Server model"""
    
    list_display = ('name', 'ip_address', 'rcon_port', 'group_count', 'created_at')
    list_filter = ('created_at', 'groups')
    search_fields = ('name', 'ip_address')
    filter_horizontal = ('groups',)  # Nice multi-select widget for groups
    readonly_fields = ('created_at', 'updated_at', 'rcon_password_encrypted')
    
    fieldsets = (
        (_('Server Information'), {
            'fields': ('name', 'ip_address', 'rcon_port')
        }),
        (_('Access Control'), {
            'fields': ('groups',)
        }),
        (_('Security'), {
            'fields': ('rcon_password_encrypted',),
            'description': _('The RCON password is encrypted and cannot be viewed. To change it, use the set_password() method.')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def group_count(self, obj):
        """Display the number of groups with access to this server"""
        return obj.groups.count()
    group_count.short_description = _('Groups')
    
    def save_model(self, request, obj, form, change):
        """
        Custom save to handle password encryption.
        Note: Password must be set via set_password() method, not through admin form.
        """
        # If this is a new server and no password is set, we need to handle it
        if not change and not obj.rcon_password_encrypted:
            # Set a placeholder - admin should update this via shell or custom form
            obj.set_password('CHANGE_ME_IMMEDIATELY')
        super().save_model(request, obj, form, change)


@admin.register(WhitelistRequest)
class WhitelistRequestAdmin(admin.ModelAdmin):
    """Admin interface for WhitelistRequest model"""
    
    list_display = ('minecraft_username', 'server', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'server')
    search_fields = ('minecraft_username', 'user__username', 'server__name')
    readonly_fields = ('created_at', 'response_log')
    
    fieldsets = (
        (_('Request Information'), {
            'fields': ('user', 'server', 'minecraft_username')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Response'), {
            'fields': ('response_log',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """
        Whitelist requests should typically be created through the web interface,
        but allow admins to create them manually if needed.
        """
        return True


# Simplified User Admin - Only Administrator and Regular User roles
class UserAdmin(BaseUserAdmin):
    """
    Simplified User Admin with clear role distinction:
    - Administrator (is_superuser=True): Full access to everything
    - Regular User (is_superuser=False): Only access assigned servers
    """
    
    list_display = ('username', 'role_display', 'is_active', 'server_access_display', 'last_login')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('username',)
    ordering = ('-is_superuser', 'username')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('username', 'password')
        }),
        (_('Role and Permissions'), {
            'fields': ('is_superuser', 'is_active'),
            'description': _(
                '<strong>Administrator</strong>: Full access to admin panel and all servers<br>'
                '<strong>Regular User</strong>: Only access assigned servers via dashboard'
            )
        }),
        (_('Server Access (Regular Users Only)'), {
            'fields': ('groups',),
            'description': _('Assign user groups to grant access to specific servers')
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_superuser', 'is_active'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('groups',)
    
    def role_display(self, obj):
        """Display user role in Chinese/English"""
        if obj.is_superuser:
            return _('Administrator')
        return _('Regular User')
    role_display.short_description = _('Role')
    role_display.admin_order_field = 'is_superuser'
    
    def server_access_display(self, obj):
        """Display server access count"""
        if obj.is_superuser:
            return _('All Servers')
        
        group_count = obj.groups.count()
        if group_count == 0:
            return _('No Access')
        return _(f'{group_count} Server(s)')
    server_access_display.short_description = _('Server Access')
    
    def save_model(self, request, obj, form, change):
        """
        Auto-set is_staff based on is_superuser for Django admin access
        """
        # Administrators need is_staff=True to access admin panel
        obj.is_staff = obj.is_superuser
        super().save_model(request, obj, form, change)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
