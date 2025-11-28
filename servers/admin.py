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


# Customize User Admin to remove email field
class UserAdmin(BaseUserAdmin):
    """Customized User Admin without email field"""
    
    # Remove email from list display
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    
    # Customize fieldsets to remove email
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Customize add form to remove email
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
