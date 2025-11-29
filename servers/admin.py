"""
Django Admin Configuration for IronGate
Registers Server and WhitelistRequest models with custom admin interfaces
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from servers.models import Server, WhitelistRequest


def is_default_group(group_name: str) -> bool:
    """
    Check if a group name matches Django's default permission group pattern.
    
    Django creates groups like "app_label | model_name" for each model.
    
    Args:
        group_name: Name of the group to check
        
    Returns:
        bool: True if group appears to be a default Django group
    """
    return " | " in group_name


from django import forms


class ServerAdminForm(forms.ModelForm):
    """Custom form for Server admin with password field"""
    
    rcon_password = forms.CharField(
        label=_('RCON Password / RCON 密码'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Enter RCON password / 输入 RCON 密码')}),
        required=False,
        help_text=_('输入新密码以更新，留空则不修改 / Enter new password to update, leave blank to keep current')
    )
    
    class Meta:
        model = Server
        exclude = ['rcon_password_encrypted']  # Exclude encrypted field, we use rcon_password instead
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing server, show password status
        if self.instance.pk and self.instance.rcon_password_encrypted:
            self.fields['rcon_password'].help_text = _(
                '✅ 密码已设置。输入新密码以更新，留空则保持不变。<br>'
                '✅ Password is set. Enter new password to update, leave blank to keep current.'
            )
    
    def save(self, commit=True):
        server = super().save(commit=False)
        
        # If password field has value, encrypt and save it
        password = self.cleaned_data.get('rcon_password')
        if password:
            server.set_password(password)
        elif not server.pk and not server.rcon_password_encrypted:
            # New server without password - set a placeholder
            server.set_password('CHANGE_ME_IMMEDIATELY')
        
        if commit:
            server.save()
            # Save many-to-many relationships
            self.save_m2m()
        
        return server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    """Admin interface for Server model"""
    
    form = ServerAdminForm
    list_display = ('name', 'ip_address', 'rcon_port', 'group_count', 'password_status', 'created_at')
    list_filter = ('created_at', 'groups')
    search_fields = ('name', 'ip_address')
    filter_horizontal = ('groups',)  # Nice multi-select widget for groups
    readonly_fields = ('created_at', 'updated_at', 'rcon_password_encrypted')
    
    fieldsets = (
        (_('Server Information'), {
            'fields': ('name', 'ip_address', 'rcon_port')
        }),
        (_('RCON Password'), {
            'fields': ('rcon_password',),
            'description': _(
                '🔒 密码将被加密存储，无法查看。<br>'
                '🔒 Password will be encrypted and cannot be viewed.'
            )
        }),
        (_('Access Control'), {
            'fields': ('groups',)
        }),
        (_('Security Info (Read Only)'), {
            'fields': ('rcon_password_encrypted',),
            'classes': ('collapse',),
            'description': _('加密后的密码数据（仅供参考）/ Encrypted password data (for reference only)')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def password_status(self, obj):
        """Display password status"""
        if obj.rcon_password_encrypted:
            return "✅ " + _("已设置")
        return "❌ " + _("未设置")
    password_status.short_description = _('Password Status')
    
    def group_count(self, obj):
        """Display the number of groups with access to this server"""
        return obj.groups.count()
    group_count.short_description = _('Groups')


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
    
    # Hide the detailed permissions section
    def get_fieldsets(self, request, obj=None):
        """Remove user_permissions field from fieldsets"""
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    
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


# Custom Group Admin with filtering
class GroupAdmin(admin.ModelAdmin):
    """
    Custom Group Admin that filters out Django's default permission groups.
    
    Only shows custom groups created for server access control.
    This project uses groups ONLY for server access control, not for Django permissions.
    """
    
    list_display = ('name', 'user_count', 'server_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    # Hide the permissions field - we only use groups for server access
    # Add help text
    fieldsets = (
        (None, {
            'fields': ('name',),
            'description': _(
                '组用于控制服务器访问权限。创建组后，在"服务器"页面将服务器分配给该组。<br>'
                'Groups are used to control server access. After creating a group, '
                'assign servers to it in the "Servers" page.'
            )
        }),
    )
    
    def get_queryset(self, request):
        """
        Override to filter out default Django groups.
        
        Only returns groups that don't match the default pattern (containing " | ").
        """
        qs = super().get_queryset(request)
        # Exclude groups with " | " in their name (Django's default format)
        return qs.exclude(name__contains=" | ")
    
    def user_count(self, obj):
        """Return number of users in this group"""
        return obj.user_set.count()
    user_count.short_description = _('Users')
    
    def server_count(self, obj):
        """Return number of servers accessible by this group"""
        return obj.servers.count()
    server_count.short_description = _('Servers')


# Unregister the default User and Group admins and register our custom ones
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
