"""
Unit tests for DisplaySettings and Announcement admin interfaces
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from servers.models import DisplaySettings, Announcement
from servers.admin import DisplaySettingsAdmin, AnnouncementAdmin


class TestDisplaySettingsAdmin(TestCase):
    """Tests for DisplaySettings admin interface"""
    
    def setUp(self):
        """Set up test client and admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
    
    def tearDown(self):
        """Clean up after each test"""
        DisplaySettings.objects.all().delete()
        User.objects.all().delete()
    
    def test_display_settings_admin_registered(self):
        """Test that DisplaySettings is registered in admin"""
        from django.contrib import admin
        assert DisplaySettings in admin.site._registry
    
    def test_display_settings_cannot_add_multiple(self):
        """Test that only one DisplaySettings instance can exist"""
        # Create first instance
        DisplaySettings.objects.create(
            show_ip_to_users=True,
            show_port_to_users=False
        )
        
        # Try to access add page
        url = reverse('admin:servers_displaysettings_add')
        response = self.client.get(url)
        
        # Should be forbidden or redirected since instance exists
        assert response.status_code in [302, 403]
    
    def test_display_settings_cannot_be_deleted(self):
        """Test that DisplaySettings cannot be deleted via admin"""
        settings = DisplaySettings.objects.create(
            show_ip_to_users=True,
            show_port_to_users=False
        )
        
        # Try to delete via admin
        url = reverse('admin:servers_displaysettings_delete', args=[settings.pk])
        response = self.client.get(url)
        
        # Should not allow deletion
        assert response.status_code in [302, 403, 404]
        
        # Verify instance still exists
        assert DisplaySettings.objects.filter(pk=settings.pk).exists()
    
    def test_display_settings_list_display(self):
        """Test that list display shows correct fields"""
        settings = DisplaySettings.objects.create(
            show_ip_to_users=True,
            show_port_to_users=False
        )
        
        url = reverse('admin:servers_displaysettings_changelist')
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert b'show_ip_to_users' in response.content or b'Show IP' in response.content


class TestAnnouncementAdmin(TestCase):
    """Tests for Announcement admin interface"""
    
    def setUp(self):
        """Set up test client and admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
    
    def tearDown(self):
        """Clean up after each test"""
        Announcement.objects.all().delete()
        User.objects.all().delete()
    
    def test_announcement_admin_registered(self):
        """Test that Announcement is registered in admin"""
        from django.contrib import admin
        assert Announcement in admin.site._registry
    
    def test_announcement_list_display(self):
        """Test that announcement list shows correct fields"""
        Announcement.objects.create(
            title="Test Announcement",
            content="Test content",
            is_active=True
        )
        
        url = reverse('admin:servers_announcement_changelist')
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert b'Test Announcement' in response.content
    
    def test_announcement_can_be_created(self):
        """Test that announcements can be created via admin"""
        url = reverse('admin:servers_announcement_add')
        response = self.client.get(url)
        
        assert response.status_code == 200
    
    def test_announcement_can_be_edited(self):
        """Test that announcements can be edited via admin"""
        announcement = Announcement.objects.create(
            title="Test",
            content="Content",
            is_active=True
        )
        
        url = reverse('admin:servers_announcement_change', args=[announcement.pk])
        response = self.client.get(url)
        
        assert response.status_code == 200
    
    def test_announcement_search_works(self):
        """Test that announcement search functionality works"""
        Announcement.objects.create(
            title="Searchable Title",
            content="Searchable content",
            is_active=True
        )
        
        url = reverse('admin:servers_announcement_changelist')
        response = self.client.get(url, {'q': 'Searchable'})
        
        assert response.status_code == 200
        assert b'Searchable Title' in response.content
    
    def test_announcement_filter_by_active(self):
        """Test that announcements can be filtered by active status"""
        Announcement.objects.create(
            title="Active",
            content="Content",
            is_active=True
        )
        Announcement.objects.create(
            title="Inactive",
            content="Content",
            is_active=False
        )
        
        url = reverse('admin:servers_announcement_changelist')
        response = self.client.get(url, {'is_active__exact': '1'})
        
        assert response.status_code == 200
