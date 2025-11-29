"""
Models for IronGate RCON Portal
Defines Server and WhitelistRequest models with encryption and validation
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from servers.utils.encryption import get_encryption_utility


class Server(models.Model):
    """
    Represents a Minecraft server with RCON access.
    
    Passwords are encrypted using Fernet symmetric encryption before storage.
    Access control is managed through Django Groups.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Server Name'),
        help_text=_('Display name for the Minecraft server')
    )
    
    ip_address = models.GenericIPAddressField(
        protocol='IPv4',
        verbose_name=_('IP Address'),
        help_text=_('IPv4 address of the Minecraft server')
    )
    
    rcon_port = models.IntegerField(
        default=25575,
        verbose_name=_('RCON Port'),
        help_text=_('RCON port number (default: 25575)')
    )
    
    rcon_password_encrypted = models.BinaryField(
        verbose_name=_('Encrypted RCON Password'),
        help_text=_('Encrypted RCON password (never stored in plaintext)')
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
        Encrypt and store the RCON password.
        
        Args:
            raw_password: The plaintext RCON password
        
        Raises:
            ValueError: If password is empty or None
        """
        if not raw_password:
            raise ValueError("RCON password cannot be empty")
        
        encryption_util = get_encryption_utility()
        self.rcon_password_encrypted = encryption_util.encrypt(raw_password)
    
    def get_password(self) -> str:
        """
        Decrypt and return the RCON password.
        
        Returns:
            str: The decrypted plaintext RCON password
        
        Raises:
            ValueError: If no password is stored
            InvalidToken: If decryption fails
        """
        if not self.rcon_password_encrypted:
            raise ValueError("No RCON password stored for this server")
        
        encryption_util = get_encryption_utility()
        return encryption_util.decrypt(self.rcon_password_encrypted)


# Minecraft username validator
minecraft_username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,16}$',
    message=_('Username must be 3-16 characters long and contain only letters, numbers, and underscores'),
    code='invalid_minecraft_username'
)


class WhitelistRequest(models.Model):
    """
    Represents a request to add a Minecraft username to a server's whitelist.
    
    Tracks the status of the request and stores RCON response logs.
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
        # Prevent duplicate whitelist requests for same server+username
        unique_together = [['server', 'minecraft_username']]
    
    def __str__(self):
        return f"{self.minecraft_username} on {self.server.name} ({self.status})"


class DisplaySettings(models.Model):
    """
    Singleton model for controlling what information is visible to users.
    Only one instance should exist in the database (pk=1).
    
    This allows administrators to control whether regular users can see
    server IP addresses and ports in the dashboard.
    """
    
    show_ip_to_users = models.BooleanField(
        default=False,
        verbose_name=_('Show IP Address to Users'),
        help_text=_('If enabled, users will see server IP addresses in the dashboard')
    )
    
    show_port_to_users = models.BooleanField(
        default=False,
        verbose_name=_('Show Port to Users'),
        help_text=_('If enabled, users will see server ports in the dashboard')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Display Settings')
        verbose_name_plural = _('Display Settings')
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance"""
        pass
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Display Settings"


class Announcement(models.Model):
    """
    System announcements displayed to all users on the dashboard.
    
    Administrators can create announcements to communicate important
    information, maintenance schedules, or usage instructions to users.
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
