"""
Django Admin Configuration for MC RCON Manager
Registers Server and WhitelistRequest models with custom admin interfaces
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from servers.models import Server, WhitelistRequest, Announcement


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
    """Custom form for Server admin with password field and custom fields editor"""
    
    rcon_password = forms.CharField(
        label=_('RCON Password / RCON 密码'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Enter RCON password / 输入 RCON 密码')}),
        required=False,
        help_text=_('输入新密码以更新，留空则不修改 / Enter new password to update, leave blank to keep current')
    )
    
    # Custom fields as individual form fields for easier editing
    modpack_name = forms.CharField(
        label=_('Modpack Name / 整合包名称'),
        required=False,
        max_length=100,
        help_text=_('Name of the modpack (e.g., "All the Mods 9") / 整合包名称（例如："All the Mods 9"）')
    )
    
    modpack_version = forms.CharField(
        label=_('Modpack Version / 整合包版本'),
        required=False,
        max_length=50,
        help_text=_('Version of the modpack (e.g., "0.2.45") / 整合包版本（例如："0.2.45"）')
    )
    
    game_version = forms.CharField(
        label=_('Game Version / 游戏版本'),
        required=False,
        max_length=50,
        help_text=_('Minecraft version (e.g., "1.20.1") / Minecraft版本（例如："1.20.1"）')
    )
    
    description = forms.CharField(
        label=_('Description / 描述'),
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('Server description / 服务器描述')
    )
    
    class Meta:
        model = Server
        exclude = ['rcon_password_encrypted', 'custom_fields']  # We handle custom_fields separately
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing server, show password status
        if self.instance.pk and self.instance.rcon_password_encrypted:
            self.fields['rcon_password'].help_text = _(
                '✅ 密码已设置。输入新密码以更新，留空则保持不变。<br>'
                '✅ Password is set. Enter new password to update, leave blank to keep current.'
            )
        
        # Load custom fields into form fields
        if self.instance.pk and self.instance.custom_fields:
            self.fields['modpack_name'].initial = self.instance.custom_fields.get('modpack_name', '')
            self.fields['modpack_version'].initial = self.instance.custom_fields.get('modpack_version', '')
            self.fields['game_version'].initial = self.instance.custom_fields.get('game_version', '')
            self.fields['description'].initial = self.instance.custom_fields.get('description', '')
    
    def save(self, commit=True):
        server = super().save(commit=False)
        
        # If password field has value, encrypt and save it
        password = self.cleaned_data.get('rcon_password')
        if password:
            server.set_password(password)
        elif not server.pk and not server.rcon_password_encrypted:
            # New server without password - set a placeholder
            server.set_password('CHANGE_ME_IMMEDIATELY')
        
        # Build custom_fields dict from form fields
        custom_fields = {}
        if self.cleaned_data.get('modpack_name'):
            custom_fields['modpack_name'] = self.cleaned_data['modpack_name']
        if self.cleaned_data.get('modpack_version'):
            custom_fields['modpack_version'] = self.cleaned_data['modpack_version']
        if self.cleaned_data.get('game_version'):
            custom_fields['game_version'] = self.cleaned_data['game_version']
        if self.cleaned_data.get('description'):
            custom_fields['description'] = self.cleaned_data['description']
        
        server.custom_fields = custom_fields
        
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
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name',)
        }),
        (_('Game Server (Shown to Users)'), {
            'fields': ('game_ip', 'game_port'),
            'description': _('玩家连接游戏服务器的地址和端口 / IP and port for players to connect to the game server')
        }),
        (_('Custom Server Information (Shown to Users)'), {
            'fields': ('modpack_name', 'modpack_version', 'game_version', 'description'),
            'description': _(
                '自定义服务器信息，将显示在服务器卡片上。留空则不显示。<br>'
                'Custom server information displayed on server cards. Leave blank to hide.'
            )
        }),
        (_('RCON Connection (Management Only)'), {
            'fields': ('ip_address', 'rcon_port'),
            'description': _('RCON管理连接信息，用户不可见 / RCON management connection, hidden from users')
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


# Inline for User Admin to show whitelist requests
class WhitelistRequestInline(admin.TabularInline):
    """Inline display of user's whitelist requests in User admin"""
    model = WhitelistRequest
    extra = 0
    readonly_fields = ('server', 'minecraft_username', 'status', 'created_at')
    fields = ('server', 'minecraft_username', 'status', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding whitelist requests from user admin"""
        return False


# Simplified User Admin - Only Administrator and Regular User roles
class UserAdmin(BaseUserAdmin):
    """
    Simplified User Admin with clear role distinction:
    - Administrator (is_superuser=True): Full access to everything
    - Regular User (is_superuser=False): Only access assigned servers
    """
    
    list_display = ('username', 'role_display', 'is_active', 'server_access_display', 'whitelist_count', 'last_login')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('username',)
    ordering = ('-is_superuser', 'username')
    inlines = [WhitelistRequestInline]
    
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
    
    def whitelist_count(self, obj):
        """Display count of whitelist requests"""
        total = obj.whitelistrequest_set.count()
        approved = obj.whitelistrequest_set.filter(status='PROCESSED').count()
        if total == 0:
            return '0'
        return f'{total} ({approved} ✓)'
    whitelist_count.short_description = _('Whitelist Requests')
    
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


# Announcement Admin
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin interface for Announcement model.
    
    Allows administrators to create and manage system announcements
    that are displayed to all users on the dashboard.
    """
    
    list_display = ('title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Announcement Content / 公告内容'), {
            'fields': ('title', 'content', 'is_active'),
            'description': _(
                '<strong>Create announcements to communicate with users.</strong><br>'
                'Supports HTML formatting. Only active announcements are displayed.<br><br>'
                '<strong>创建公告以与用户沟通。</strong><br>'
                '支持HTML格式。只有活跃的公告会被显示。'
            )
        }),
        (_('Timestamps / 时间戳'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Order announcements by creation date (newest first).
        """
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')


# Customize admin site headers
admin.site.site_header = _("MC RCON Manager Admin")
admin.site.site_title = _("MC RCON Manager")
admin.site.index_title = _("Welcome to MC RCON Manager Admin Panel")


# Register custom admin URLs
from django.urls import path
from servers.admin_views import ungrouped_users_view


def get_admin_urls(urls):
    """Add custom admin URLs"""
    custom_urls = [
        path('ungrouped-users/', ungrouped_users_view, name='ungrouped_users'),
    ]
    return custom_urls + urls


admin.site.get_urls = lambda: get_admin_urls(admin.site.get_urls())
