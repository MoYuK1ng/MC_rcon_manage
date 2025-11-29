"""
Property-based tests for DisplaySettings model
Tests correctness properties using Hypothesis
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from servers.models import DisplaySettings


class TestDisplaySettingsProperties(TestCase):
    """Property-based tests for DisplaySettings model"""
    
    def tearDown(self):
        """Clean up after each test"""
        DisplaySettings.objects.all().delete()
    
    @given(
        show_ip=st.booleans(),
        show_port=st.booleans()
    )
    def test_property_singleton_behavior(self, show_ip, show_port):
        """
        **Feature: admin-display-settings, Property 9: DisplaySettings singleton behavior**
        
        For any sequence of DisplaySettings save operations, only one instance with pk=1
        should exist in the database, and all save operations should update this single
        instance rather than creating new records.
        
        Validates: Requirements 2.1, 2.5
        """
        # Create first instance
        settings1 = DisplaySettings(
            show_ip_to_users=show_ip,
            show_port_to_users=show_port
        )
        settings1.save()
        
        # Verify pk is 1
        assert settings1.pk == 1
        
        # Verify only one instance exists
        assert DisplaySettings.objects.count() == 1
        
        # Create second instance with different values
        settings2 = DisplaySettings(
            show_ip_to_users=not show_ip,
            show_port_to_users=not show_port
        )
        settings2.save()
        
        # Verify pk is still 1
        assert settings2.pk == 1
        
        # Verify still only one instance exists
        assert DisplaySettings.objects.count() == 1
        
        # Verify the values were updated (not a new record)
        retrieved = DisplaySettings.objects.get(pk=1)
        assert retrieved.show_ip_to_users == (not show_ip)
        assert retrieved.show_port_to_users == (not show_port)
    
    @given(
        show_ip=st.booleans(),
        show_port=st.booleans()
    )
    def test_property_settings_persistence(self, show_ip, show_port):
        """
        **Feature: admin-display-settings, Property 2: Display settings persistence**
        
        For any display settings modification, saving the settings to the database
        and then retrieving them should return the same values.
        
        Validates: Requirements 2.5
        """
        # Create and save settings
        settings = DisplaySettings(
            show_ip_to_users=show_ip,
            show_port_to_users=show_port
        )
        settings.save()
        
        # Retrieve settings
        retrieved = DisplaySettings.get_settings()
        
        # Verify values match
        assert retrieved.show_ip_to_users == show_ip
        assert retrieved.show_port_to_users == show_port
        assert retrieved.pk == 1
    
    def test_get_settings_creates_if_not_exists(self):
        """
        Test that get_settings() creates default instance if none exists
        """
        # Ensure no settings exist
        DisplaySettings.objects.all().delete()
        
        # Call get_settings
        settings = DisplaySettings.get_settings()
        
        # Verify instance was created with defaults
        assert settings.pk == 1
        assert settings.show_ip_to_users == False
        assert settings.show_port_to_users == False
        assert DisplaySettings.objects.count() == 1
    
    def test_delete_prevention(self):
        """
        Test that DisplaySettings cannot be deleted
        """
        settings = DisplaySettings.get_settings()
        settings.delete()
        
        # Verify instance still exists
        assert DisplaySettings.objects.filter(pk=1).exists()



class TestRCONIndependenceProperty(TestCase):
    """Property-based test for RCON independence from display settings"""
    
    def tearDown(self):
        """Clean up after each test"""
        from servers.models import Server
        from django.contrib.auth.models import Group
        Server.objects.all().delete()
        DisplaySettings.objects.all().delete()
        Group.objects.all().delete()
    
    @given(
        show_ip=st.booleans(),
        show_port=st.booleans()
    )
    @settings(max_examples=50)
    def test_property_rcon_independence(self, show_ip, show_port):
        """
        **Feature: admin-display-settings, Property 3: RCON functionality independence**
        
        For any display settings configuration, RCON connections and commands should
        function correctly regardless of whether IP and port information is visible
        to users in the dashboard.
        
        Validates: Requirements 1.5, 5.1
        """
        from servers.models import Server
        from django.contrib.auth.models import Group
        
        # Create server
        group = Group.objects.create(name='TestGroup')
        server = Server.objects.create(
            name="Test Server",
            ip_address="192.168.1.100",
            rcon_port=25575
        )
        server.set_password("testpass")
        server.groups.add(group)
        server.save()
        
        # Set display settings
        settings = DisplaySettings.get_settings()
        settings.show_ip_to_users = show_ip
        settings.show_port_to_users = show_port
        settings.save()
        
        # Verify server data is accessible regardless of display settings
        retrieved_server = Server.objects.get(pk=server.pk)
        assert retrieved_server.ip_address == "192.168.1.100"
        assert retrieved_server.rcon_port == 25575
        assert retrieved_server.get_password() == "testpass"
        
        # Verify server can be used for RCON (data is intact)
        assert retrieved_server.ip_address is not None
        assert retrieved_server.rcon_port is not None
        assert retrieved_server.rcon_password_encrypted is not None
