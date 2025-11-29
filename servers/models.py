"""
mc rcon 管理器的数据模型
定义了带有加密和验证功能的服务器和白名单请求模型
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from servers.utils.encryption import get_encryption_utility


class Server(models.Model):
    """
    表示一个具有rcon访问权限的minecraft服务器
    
    密码在存储前使用fernet对称加密进行加密
    访问控制通过django组进行管理
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Server Name'),
        help_text=_('Display name for the Minecraft server')
    )
    
    # rcon连接信息（用于管理，对用户隐藏）
    ip_address = models.GenericIPAddressField(
        protocol='IPv4',
        verbose_name=_('RCON IP Address'),
        help_text=_('IPv4 address for RCON connection (management only)')
    )
    
    rcon_port = models.IntegerField(
        default=25575,
        verbose_name=_('RCON Port'),
        help_text=_('RCON port number (default: 25575, management only)')
    )
    
    # 游戏服务器信息（供玩家连接，向用户显示）
    game_ip = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Game Server IP'),
        help_text=_('IP or domain for players to connect (e.g., play.example.com)')
    )
    
    game_port = models.IntegerField(
        blank=True,
        null=True,
        default=25565,
        verbose_name=_('Game Server Port'),
        help_text=_('Port for players to connect (default: 25565)')
    )
    
    rcon_password_encrypted = models.BinaryField(
        verbose_name=_('Encrypted RCON Password'),
        help_text=_('Encrypted RCON password (never stored in plaintext)')
    )
    
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Custom Fields'),
        help_text=_('Custom metadata (modpack name, game version, description, etc.)')
    )
    
    groups = models.ManyToManyField(
        Group,
        related_name='servers',
        verbose_name=_('Access Groups'),
        help_text=_('User groups that can access this server'),
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.ip_address}:{self.rcon_port})"
    
    def set_password(self, raw_password: str) -> None:
        """
        加密并存储rcon密码
        
        参数:
            raw_password: 明文rcon密码
        
        异常:
            ValueError: 如果密码为空或无效
        """
        if not raw_password:
            raise ValueError("RCON password cannot be empty")
        
        encryption_util = get_encryption_utility()
        self.rcon_password_encrypted = encryption_util.encrypt(raw_password)
    
    def get_password(self) -> str:
        """
        解密并返回rcon密码
        
        返回:
            str: 解密后的明文rcon密码
        
        异常:
            ValueError: 如果没有存储密码
            InvalidToken: 如果解密失败
        """
        if not self.rcon_password_encrypted:
            raise ValueError("No RCON password stored for this server")
        
        encryption_util = get_encryption_utility()
        return encryption_util.decrypt(self.rcon_password_encrypted)


# minecraft用户名验证器
minecraft_username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,16}$',
    message=_('Username must be 3-16 characters long and contain only letters, numbers, and underscores'),
    code='invalid_minecraft_username'
)


class WhitelistRequest(models.Model):
    """
    表示将minecraft用户名添加到服务器白名单的请求
    
    跟踪请求状态并存储rcon响应日志
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        PROCESSED = 'PROCESSED', _('Processed')
        FAILED = 'FAILED', _('Failed')
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        help_text=_('User who submitted the whitelist request')
    )
    
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        verbose_name=_('Server'),
        help_text=_('Target Minecraft server')
    )
    
    minecraft_username = models.CharField(
        max_length=16,
        validators=[minecraft_username_validator],
        verbose_name=_('Minecraft Username'),
        help_text=_('Minecraft username to whitelist (3-16 alphanumeric characters and underscores)')
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status'),
        help_text=_('Current status of the whitelist request')
    )
    
    response_log = models.TextField(
        blank=True,
        verbose_name=_('Response Log'),
        help_text=_('RCON server response or error message')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Whitelist Request')
        verbose_name_plural = _('Whitelist Requests')
        ordering = ['-created_at']
        # 防止同一服务器和用户名的重复白名单请求
        unique_together = [['server', 'minecraft_username']]
    
    def __str__(self):
        return f"{self.minecraft_username} on {self.server.name} ({self.status})"


class Announcement(models.Model):
    """
    在仪表板上向所有用户显示的系统公告
    
    管理员可以创建公告来向用户传达重要信息、维护计划或使用说明
    """
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
        help_text=_('Announcement title (supports Chinese and English)')
    )
    
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Announcement content (supports HTML formatting)')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Only active announcements are displayed to users')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
