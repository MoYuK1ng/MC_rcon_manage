"""
Unit Tests for IronGate Models
Tests Server and WhitelistRequest models with specific examples and edge cases
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from servers.models import Server, WhitelistRequest
from cryptography.fernet import InvalidToken


@pytest.mark.unit
class TestServerModel(TestCase):
    """Unit tests for Server model"""
    
    def setUp(self):
        """Set up test data"""
        self.group = Group.objects.create(name='TestGroup')
        self.server = Server(
            name='Test Server',
            ip_address='192.168.1.100',
            rcon_port=25575
        )
    
    def test_server_creation(self):
        """Test creating a server with all required fields"""
        self.server.set_password('test_password_123')
        self.server.save()
        
        self.assertEqual(self.server.name, 'Test Server')
        self.assertEqual(self.server.ip_address, '192.168.1.100')
        self.assertEqual(self.server.rcon_port, 25575)
        self.assertIsNotNone(self.server.rcon_password_encrypted)
    
    def test_server_str_representation(self):
        """Test string representation of server"""
        self.server.set_password('test')
        self.server.save()
        
        expected = "Test Server (192.168.1.100:25575)"
        self.assertEqual(str(self.server), expected)
    
    def test_set_password_encrypts_password(self):
        """Test that set_password encrypts the password"""
        password = 'my_secret_password'
        self.server.set_password(password)
        
        # Password should be encrypted (bytes)
        self.assertIsInstance(self.server.rcon_password_encrypted, bytes)
        # Encrypted password should not equal plaintext
        self.assertNotEqual(self.server.rcon_password_encrypted, password.encode())
    
    def test_get_password_decrypts_password(self):
        """Test that get_password correctly decrypts the password"""
        password = 'my_secret_password'
        self.server.set_password(password)
        self.server.save()
        
        # Retrieve and decrypt
        decrypted = self.server.get_password()
        self.assertEqual(decrypted, password)
    
    def test_set_password_empty_raises_error(self):
        """Test that setting an empty password raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.server.set_password('')
        
        self.assertIn('cannot be empty', str(context.exception))
    
    def test_set_password_none_raises_error(self):
        """Test that setting None as password raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.server.set_password(None)
        
        self.assertIn('cannot be empty', str(context.exception))
    
    def test_get_password_without_setting_raises_error(self):
        """Test that getting password without setting it raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.server.get_password()
        
        self.assertIn('No RCON password stored', str(context.exception))
    
    def test_server_groups_relationship(self):
        """Test ManyToMany relationship with Groups"""
        self.server.set_password('test')
        self.server.save()
        
        # Add group
        self.server.groups.add(self.group)
        
        # Verify relationship
        self.assertEqual(self.server.groups.count(), 1)
        self.assertIn(self.group, self.server.groups.all())
        
        # Verify reverse relationship
        self.assertIn(self.server, self.group.servers.all())
    
    def test_server_default_port(self):
        """Test that default RCON port is 25575"""
        server = Server(name='Default Port Server', ip_address='127.0.0.1')
        self.assertEqual(server.rcon_port, 25575)


@pytest.mark.unit
class TestWhitelistRequestModel(TestCase):
    """Unit tests for WhitelistRequest model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.server = Server(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.save()
    
    def test_whitelist_request_creation(self):
        """Test creating a whitelist request"""
        request = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='TestPlayer123'
        )
        
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.server, self.server)
        self.assertEqual(request.minecraft_username, 'TestPlayer123')
        self.assertEqual(request.status, WhitelistRequest.Status.PENDING)
    
    def test_whitelist_request_str_representation(self):
        """Test string representation of whitelist request"""
        request = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='Player1'
        )
        
        expected = "Player1 on Test Server (PENDING)"
        self.assertEqual(str(request), expected)
    
    def test_valid_minecraft_username_accepted(self):
        """Test that valid Minecraft usernames are accepted"""
        valid_usernames = [
            'Steve',
            'Alex',
            'Player123',
            'test_user',
            'ABC',
            'a1b2c3d4e5f6g7h8',  # 16 characters (max)
        ]
        
        for username in valid_usernames:
            request = WhitelistRequest(
                user=self.user,
                server=self.server,
                minecraft_username=username
            )
            try:
                request.full_clean()  # This runs validators
            except ValidationError:
                self.fail(f"Valid username '{username}' was rejected")
    
    def test_invalid_minecraft_username_rejected(self):
        """Test that invalid Minecraft usernames are rejected"""
        invalid_usernames = [
            'ab',  # Too short (2 characters)
            'a' * 17,  # Too long (17 characters)
            'user name',  # Contains space
            'user@name',  # Contains @
            'user-name',  # Contains hyphen
            'user.name',  # Contains dot
            'user;DROP TABLE',  # SQL injection attempt
            'user&whoami',  # Command injection attempt
            'user|ls',  # Pipe character
        ]
        
        for username in invalid_usernames:
            request = WhitelistRequest(
                user=self.user,
                server=self.server,
                minecraft_username=username
            )
            with self.assertRaises(ValidationError) as context:
                request.full_clean()
            
            self.assertIn('minecraft_username', context.exception.message_dict,
                         f"Username '{username}' should have been rejected")
    
    def test_whitelist_request_status_choices(self):
        """Test that status can be set to all valid choices"""
        request = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='TestPlayer'
        )
        
        # Test all status choices
        for status_value, status_label in WhitelistRequest.Status.choices:
            request.status = status_value
            request.save()
            request.refresh_from_db()
            self.assertEqual(request.status, status_value)
    
    def test_whitelist_request_response_log(self):
        """Test that response_log can store RCON responses"""
        request = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='TestPlayer',
            response_log='Added TestPlayer to whitelist'
        )
        
        self.assertEqual(request.response_log, 'Added TestPlayer to whitelist')
    
    def test_whitelist_request_foreign_key_cascade(self):
        """Test that deleting user or server cascades to whitelist requests"""
        request = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='TestPlayer'
        )
        request_id = request.id
        
        # Delete user
        self.user.delete()
        
        # Request should be deleted
        with self.assertRaises(WhitelistRequest.DoesNotExist):
            WhitelistRequest.objects.get(id=request_id)
    
    def test_whitelist_request_ordering(self):
        """Test that whitelist requests are ordered by created_at descending"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create multiple requests with explicit timestamps
        now = timezone.now()
        
        request1 = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='Player1'
        )
        request1.created_at = now - timedelta(seconds=2)
        request1.save()
        
        request2 = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='Player2'
        )
        request2.created_at = now - timedelta(seconds=1)
        request2.save()
        
        request3 = WhitelistRequest.objects.create(
            user=self.user,
            server=self.server,
            minecraft_username='Player3'
        )
        request3.created_at = now
        request3.save()
        
        # Get all requests
        requests = list(WhitelistRequest.objects.all())
        
        # Should be ordered newest first
        self.assertEqual(requests[0], request3)
        self.assertEqual(requests[1], request2)
        self.assertEqual(requests[2], request1)


@pytest.mark.unit
class TestModelRelationships(TestCase):
    """Unit tests for model relationships"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')
        
        self.server1 = Server(name='Server1', ip_address='192.168.1.1', rcon_port=25575)
        self.server1.set_password('pass1')
        self.server1.save()
        self.server1.groups.add(self.group1)
        
        self.server2 = Server(name='Server2', ip_address='192.168.1.2', rcon_port=25575)
        self.server2.set_password('pass2')
        self.server2.save()
        self.server2.groups.add(self.group2)
    
    def test_user_group_server_relationship(self):
        """Test the User -> Group -> Server relationship chain"""
        # Add user1 to group1
        self.user1.groups.add(self.group1)
        
        # User1 should have access to server1 through group1
        accessible_servers = Server.objects.filter(groups__in=self.user1.groups.all())
        self.assertIn(self.server1, accessible_servers)
        self.assertNotIn(self.server2, accessible_servers)
    
    def test_user_multiple_groups_server_access(self):
        """Test user with multiple groups has access to all linked servers"""
        # Add user1 to both groups
        self.user1.groups.add(self.group1, self.group2)
        
        # User1 should have access to both servers
        accessible_servers = Server.objects.filter(
            groups__in=self.user1.groups.all()
        ).distinct()
        
        self.assertIn(self.server1, accessible_servers)
        self.assertIn(self.server2, accessible_servers)
        self.assertEqual(accessible_servers.count(), 2)
    
    def test_whitelist_request_user_server_relationship(self):
        """Test WhitelistRequest relationships with User and Server"""
        request = WhitelistRequest.objects.create(
            user=self.user1,
            server=self.server1,
            minecraft_username='TestPlayer'
        )
        
        # Verify forward relationships
        self.assertEqual(request.user, self.user1)
        self.assertEqual(request.server, self.server1)
        
        # Verify reverse relationships
        self.assertIn(request, self.user1.whitelistrequest_set.all())
        self.assertIn(request, self.server1.whitelistrequest_set.all())
