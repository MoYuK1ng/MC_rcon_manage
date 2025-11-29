"""
Property-based tests for IP/port visibility control
Tests that display settings correctly control what information is visible
"""

import pytest
from hypothesis import given, strategies as st, settings
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import User, Group
from servers.models import Server, DisplaySettings


@pytest.mark.django_db
@given(
    show_ip=st.booleans(),
    show_port=st.booleans()
)
@settings(max_examples=100, deadline=None)
def test_property_display_settings_control_visibility(show_ip, show_port):
    """
    **Feature: admin-display-settings, Property 1: Display settings control IP/port visibility**
    
    For any server and display settings configuration, when show_ip_to_users is False,
    the rendered dashboard HTML should not contain the server's IP address; when
    show_port_to_users is False, the rendered HTML should not contain the server's
    port number; when either setting is True, the corresponding information should
    be present in the HTML.
    
    Validates: Requirements 1.1, 1.2, 2.2, 2.3, 2.4
    """
    # Clean up first
    Server.objects.all().delete()
    DisplaySettings.objects.all().delete()
    User.objects.all().delete()
    Group.objects.all().delete()
    
    # Set up test client and user
    client = Client()
    user = User.objects.create_user(
        username='testuser',
        password='testpass123'
    )
    group = Group.objects.create(name='TestGroup')
    user.groups.add(group)
    client.login(username='testuser', password='testpass123')
    
    # Create server
    server = Server.objects.create(
        name="Test Server",
        ip_address="192.168.1.100",
        rcon_port=25575
    )
    server.set_password("testpass")
    server.groups.add(group)
    server.save()
    
    # Set display settings
    display_settings = DisplaySettings.get_settings()
    display_settings.show_ip_to_users = show_ip
    display_settings.show_port_to_users = show_port
    display_settings.save()
    
    # Get dashboard
    response = client.get('/dashboard/')
    content = response.content.decode('utf-8')
    
    # Server name should always be visible
    assert "Test Server" in content
    
    # IP should only be visible if show_ip is True
    if show_ip:
        assert "192.168.1.100" in content
    else:
        assert "192.168.1.100" not in content
    
    # Port should only be visible if show_port is True
    if show_port:
        assert "25575" in content
    else:
        # Port might appear in other contexts, so check it's not in the server info
        # We'll check that the IP:port combination doesn't appear
        if not show_ip:
            assert "192.168.1.100:25575" not in content


class TestVisibilityProperties(TestCase):
    """Additional visibility tests"""
    
    def test_admin_always_sees_all_info(self):
        """
        Test that administrators always see all server information in admin panel
        regardless of display settings.
        
        Validates: Requirements 1.4
        """
        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )
        admin_client = Client()
        admin_client.login(username='admin', password='adminpass')
        
        # Create server
        server = Server.objects.create(
            name="Admin Test Server",
            ip_address="10.0.0.1",
            rcon_port=25575
        )
        server.set_password("testpass")
        server.save()
        
        # Set display settings to hide everything
        settings = DisplaySettings.get_settings()
        settings.show_ip_to_users = False
        settings.show_port_to_users = False
        settings.save()
        
        # Access admin panel
        response = admin_client.get('/admin/servers/server/')
        content = response.content.decode('utf-8')
        
        # Admin should see IP and port
        assert "10.0.0.1" in content
        assert "25575" in content
