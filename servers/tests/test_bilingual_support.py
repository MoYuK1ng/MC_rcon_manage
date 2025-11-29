"""
Unit tests for bilingual support (English and Chinese)
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from servers.models import Server, Announcement, DisplaySettings


class TestBilingualSupport(TestCase):
    """Tests for bilingual support in templates and announcements"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.group = Group.objects.create(name='TestGroup')
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass123')
        
        # Create test server
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
        Announcement.objects.all().delete()
        DisplaySettings.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
    
    def test_english_template_renders_correctly(self):
        """
        Test that English template renders correctly with server data.
        
        Validates: Requirements 4.5
        """
        response = self.client.get('/dashboard/')
        
        assert response.status_code == 200
        assert b'Test Server' in response.content
        assert b'Server Dashboard' in response.content or b'dashboard' in response.content.lower()
    
    def test_chinese_template_renders_correctly(self):
        """
        Test that Chinese template renders correctly with server data.
        
        Validates: Requirements 4.5
        """
        # Set Chinese language cookie
        self.client.cookies['user_lang'] = 'zh'
        
        response = self.client.get('/dashboard/')
        
        assert response.status_code == 200
        assert b'Test Server' in response.content
        # Check for Chinese text
        assert '服务器'.encode('utf-8') in response.content or '仪表板'.encode('utf-8') in response.content
    
    def test_chinese_content_in_announcements_displays_correctly(self):
        """
        Test that Chinese content in announcements is displayed correctly.
        
        Validates: Requirements 4.5
        """
        # Create announcement with Chinese content
        announcement = Announcement.objects.create(
            title="系统维护通知",
            content="服务器将在今晚进行维护，请提前保存您的游戏进度。",
            is_active=True
        )
        
        # Get dashboard
        response = self.client.get('/dashboard/')
        content = response.content.decode('utf-8')
        
        # Verify Chinese content is present
        assert "系统维护通知" in content
        assert "服务器将在今晚进行维护" in content
    
    def test_mixed_language_announcements(self):
        """
        Test that announcements with mixed English and Chinese content work correctly.
        
        Validates: Requirements 4.5
        """
        # Create announcement with mixed content
        announcement = Announcement.objects.create(
            title="Server Maintenance / 服务器维护",
            content="<p>The server will be down for maintenance.</p><p>服务器将进行维护。</p>",
            is_active=True
        )
        
        # Get dashboard
        response = self.client.get('/dashboard/')
        content = response.content.decode('utf-8')
        
        # Verify both English and Chinese content is present
        assert "Server Maintenance" in content
        assert "服务器维护" in content
        assert "maintenance" in content
        assert "维护" in content
    
    def test_unicode_characters_preserved(self):
        """
        Test that Unicode characters (including Chinese) are preserved in database.
        
        Validates: Requirements 4.5
        """
        # Create announcement with various Unicode characters
        announcement = Announcement.objects.create(
            title="测试公告 🎮",
            content="这是一个测试：中文、English、日本語、한국어",
            is_active=True
        )
        
        # Retrieve from database
        retrieved = Announcement.objects.get(pk=announcement.pk)
        
        # Verify Unicode is preserved
        assert retrieved.title == "测试公告 🎮"
        assert retrieved.content == "这是一个测试：中文、English、日本語、한국어"
    
    def test_html_in_chinese_content(self):
        """
        Test that HTML formatting works with Chinese content.
        
        Validates: Requirements 3.5, 4.5
        """
        # Create announcement with HTML and Chinese
        announcement = Announcement.objects.create(
            title="重要通知",
            content="<strong>重要：</strong>服务器将在<em>今晚8点</em>进行维护。<br>请提前保存进度。",
            is_active=True
        )
        
        # Get dashboard
        response = self.client.get('/dashboard/')
        content = response.content.decode('utf-8')
        
        # Verify HTML tags are present (not escaped)
        assert "<strong>" in content
        assert "<em>" in content
        assert "<br>" in content or "<br/>" in content
        
        # Verify Chinese content is present
        assert "重要" in content
        assert "服务器" in content
