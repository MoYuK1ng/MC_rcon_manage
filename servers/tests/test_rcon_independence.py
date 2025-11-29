"""
Tests to verify RCON functionality is independent of display settings
"""

import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User, Group
from servers.models import Server, DisplaySettings
from servers.services.rcon_manager import RconHandler


class TestRCONIndependence(TestCase):
    """Tests that RCON functionality works regardless of display settings"""
    
    def setUp(self):
        """Set up test data"""
        self.group = Group.objects.create(name='TestGroup')
        self.server = Server.objects.create(
            name="Test Server",
            ip_address="192.168.1.100",
            rcon_port=25575
        )
        self.server.set_password("testpass")
        self.server.groups.add(self.group)
        self.server.save()
    
    def tearDown(self):
        """Clean up after each test"""
        Server.objects.all().delete()
        DisplaySettings.objects.all().delete()
        Group.objects.all().delete()
    
    def test_rcon_connection_with_hidden_ip_port(self):
        """
        Test that RCON connections work when IP and port are hidden from users.
        
        Validates: Requirements 1.5, 5.1
        """
        # Set display settings to hide IP and port
        settings = DisplaySettings.get_settings()
        settings.show_ip_to_users = False
        settings.show_port_to_users = False
        settings.save()
        
        # Create RCON handler
        handler = RconHandler(self.server)
        
        # Verify server still has IP and port accessible
        assert self.server.ip_address == "192.168.1.100"
        assert self.server.rcon_port == 25575
        
        # Verify handler can access server credentials
        assert handler.host == "192.168.1.100"
        assert handler.port == 25575
        
        # Verify password is accessible
        password = self.server.get_password()
        assert password == "testpass"
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_rcon_whitelist_with_hidden_ip_port(self, mock_rcon):
        """
        Test that whitelist commands work when IP and port are hidden.
        
        Validates: Requirements 1.5, 5.1
        """
        # Set display settings to hide IP and port
        settings = DisplaySettings.get_settings()
        settings.show_ip_to_users = False
        settings.show_port_to_users = False
        settings.save()
        
        # Mock RCON client
        mock_instance = Mock()
        mock_instance.command.return_value = "Added TestPlayer to whitelist"
        mock_rcon.return_value.__enter__.return_value = mock_instance
        
        # Create RCON handler
        handler = RconHandler(self.server)
        
        # Try to add to whitelist
        result = handler.add_whitelist("TestPlayer")
        
        # Verify RCON connection was attempted
        mock_rcon.assert_called_once()
        
        # Verify result is successful
        assert result['success'] == True
    
    def test_server_model_retains_ip_port(self):
        """
        Test that Server model always retains IP and port data regardless of display settings.
        
        Validates: Requirements 1.5
        """
        # Set display settings to hide IP and port
        settings = DisplaySettings.get_settings()
        settings.show_ip_to_users = False
        settings.show_port_to_users = False
        settings.save()
        
        # Retrieve server from database
        server = Server.objects.get(pk=self.server.pk)
        
        # Verify IP and port are still accessible
        assert server.ip_address == "192.168.1.100"
        assert server.rcon_port == 25575
        
        # Verify password is still accessible
        assert server.get_password() == "testpass"
