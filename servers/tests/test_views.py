"""
Unit Tests for Views
Tests dashboard, player list, and whitelist views with access control
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

from servers.models import Server, WhitelistRequest


@pytest.mark.unit
class TestDashboardView(TestCase):
    """Unit tests for DashboardView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create groups
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')
        
        # Assign users to groups
        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group2)
        
        # Create servers
        self.server1 = Server(name='Server1', ip_address='192.168.1.1', rcon_port=25575)
        self.server1.set_password('pass1')
        self.server1.save()
        self.server1.groups.add(self.group1)
        
        self.server2 = Server(name='Server2', ip_address='192.168.1.2', rcon_port=25575)
        self.server2.set_password('pass2')
        self.server2.save()
        self.server2.groups.add(self.group2)
    
    def test_dashboard_requires_authentication(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_dashboard_shows_only_accessible_servers(self):
        """Test that dashboard only shows servers user has access to"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('servers', response.context)
        
        servers = list(response.context['servers'])
        self.assertIn(self.server1, servers)
        self.assertNotIn(self.server2, servers)
    
    def test_dashboard_shows_no_servers_for_user_without_groups(self):
        """Test that users without groups see no servers"""
        user3 = User.objects.create_user(username='user3', password='pass123')
        self.client.login(username='user3', password='pass123')
        
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        servers = list(response.context['servers'])
        self.assertEqual(len(servers), 0)
    
    def test_dashboard_deduplicates_servers(self):
        """Test that servers linked to multiple groups appear only once"""
        # Add server1 to both groups
        self.server1.groups.add(self.group2)
        
        # Add user1 to both groups
        self.user1.groups.add(self.group2)
        
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('dashboard'))
        
        servers = list(response.context['servers'])
        # Count how many times server1 appears
        server1_count = servers.count(self.server1)
        self.assertEqual(server1_count, 1, "Server should appear only once")


@pytest.mark.unit
class TestPlayerListView(TestCase):
    """Unit tests for PlayerListView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.group = Group.objects.create(name='TestGroup')
        self.user.groups.add(self.group)
        
        self.server = Server(name='TestServer', ip_address='127.0.0.1', rcon_port=25575)
        self.server.set_password('testpass')
        self.server.save()
        self.server.groups.add(self.group)
        
        # Create a server the user doesn't have access to
        self.other_group = Group.objects.create(name='OtherGroup')
        self.other_server = Server(name='OtherServer', ip_address='127.0.0.2', rcon_port=25575)
        self.other_server.set_password('otherpass')
        self.other_server.save()
        self.other_server.groups.add(self.other_group)
    
    def test_player_list_requires_authentication(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse('player_list', args=[self.server.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    @patch('servers.views.RconHandler')
    def test_player_list_returns_players(self, mock_handler_class):
        """Test that player list view returns player data"""
        # Mock RCON handler
        mock_handler = MagicMock()
        mock_handler.get_players.return_value = {
            'success': True,
            'players': ['Steve', 'Alex'],
            'message': 'Found 2 players'
        }
        mock_handler_class.return_value = mock_handler
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('player_list', args=[self.server.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('players', response.context)
        self.assertEqual(response.context['players'], ['Steve', 'Alex'])
    
    def test_player_list_denies_unauthorized_access(self):
        """Test that users cannot access servers they don't have permission for"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('player_list', args=[self.other_server.id]))
        
        self.assertEqual(response.status_code, 403)
    
    @patch('servers.views.RconHandler')
    def test_player_list_handles_rcon_errors(self, mock_handler_class):
        """Test that player list view handles RCON errors gracefully"""
        # Mock RCON handler with error
        mock_handler = MagicMock()
        mock_handler.get_players.return_value = {
            'success': False,
            'players': [],
            'message': 'Connection timeout'
        }
        mock_handler_class.return_value = mock_handler
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('player_list', args=[self.server.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['success'])
        self.assertIn('Connection timeout', response.context['message'])


@pytest.mark.unit
class TestWhitelistAddView(TestCase):
    """Unit tests for WhitelistAddView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.group = Group.objects.create(name='TestGroup')
        self.user.groups.add(self.group)
        
        self.server = Server(name='TestServer', ip_address='127.0.0.1', rcon_port=25575)
        self.server.set_password('testpass')
        self.server.save()
        self.server.groups.add(self.group)
        
        # Create a server the user doesn't have access to
        self.other_group = Group.objects.create(name='OtherGroup')
        self.other_server = Server(name='OtherServer', ip_address='127.0.0.2', rcon_port=25575)
        self.other_server.set_password('otherpass')
        self.other_server.save()
        self.other_server.groups.add(self.other_group)
    
    def test_whitelist_add_requires_authentication(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.post(reverse('whitelist_add', args=[self.server.id]), {
            'minecraft_username': 'TestPlayer'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    @patch('servers.views.RconHandler')
    def test_whitelist_add_success(self, mock_handler_class):
        """Test successful whitelist addition"""
        # Mock RCON handler
        mock_handler = MagicMock()
        mock_handler.add_whitelist.return_value = {
            'success': True,
            'message': 'Added TestPlayer to whitelist'
        }
        mock_handler_class.return_value = mock_handler
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('whitelist_add', args=[self.server.id]), {
            'minecraft_username': 'TestPlayer'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verify WhitelistRequest was created
        request = WhitelistRequest.objects.get(minecraft_username='TestPlayer')
        self.assertEqual(request.status, WhitelistRequest.Status.PROCESSED)
    
    @patch('servers.views.RconHandler')
    def test_whitelist_add_handles_rcon_failure(self, mock_handler_class):
        """Test whitelist addition when RCON fails"""
        # Mock RCON handler with failure
        mock_handler = MagicMock()
        mock_handler.add_whitelist.return_value = {
            'success': False,
            'message': 'Connection timeout'
        }
        mock_handler_class.return_value = mock_handler
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('whitelist_add', args=[self.server.id]), {
            'minecraft_username': 'TestPlayer'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify WhitelistRequest was created with FAILED status
        request = WhitelistRequest.objects.get(minecraft_username='TestPlayer')
        self.assertEqual(request.status, WhitelistRequest.Status.FAILED)
    
    def test_whitelist_add_validates_username(self):
        """Test that invalid usernames are rejected"""
        self.client.login(username='testuser', password='pass123')
        
        # Try with invalid username (contains space)
        response = self.client.post(reverse('whitelist_add', args=[self.server.id]), {
            'minecraft_username': 'Invalid User'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify no WhitelistRequest was created
        self.assertEqual(WhitelistRequest.objects.count(), 0)
    
    def test_whitelist_add_denies_unauthorized_access(self):
        """Test that users cannot whitelist on servers they don't have access to"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('whitelist_add', args=[self.other_server.id]), {
            'minecraft_username': 'TestPlayer'
        })
        
        self.assertEqual(response.status_code, 403)
    
    def test_whitelist_add_rejects_empty_username(self):
        """Test that empty usernames are rejected"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(reverse('whitelist_add', args=[self.server.id]), {
            'minecraft_username': ''
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WhitelistRequest.objects.count(), 0)


@pytest.mark.unit
class TestAccessControlSecurity(TestCase):
    """Security tests for access control"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create User A with Group A
        self.user_a = User.objects.create_user(username='userA', password='pass123')
        self.group_a = Group.objects.create(name='GroupA')
        self.user_a.groups.add(self.group_a)
        
        # Create User B with Group B
        self.user_b = User.objects.create_user(username='userB', password='pass123')
        self.group_b = Group.objects.create(name='GroupB')
        self.user_b.groups.add(self.group_b)
        
        # Create Server A (Group A only)
        self.server_a = Server(name='ServerA', ip_address='192.168.1.1', rcon_port=25575)
        self.server_a.set_password('passA')
        self.server_a.save()
        self.server_a.groups.add(self.group_a)
        
        # Create Server B (Group B only)
        self.server_b = Server(name='ServerB', ip_address='192.168.1.2', rcon_port=25575)
        self.server_b.set_password('passB')
        self.server_b.save()
        self.server_b.groups.add(self.group_b)
    
    def test_user_a_cannot_access_server_b_player_list(self):
        """Test that User A (Group A) cannot access Server B (Group B) player list"""
        self.client.login(username='userA', password='pass123')
        response = self.client.get(reverse('player_list', args=[self.server_b.id]))
        
        self.assertEqual(response.status_code, 403, 
                        "User A should not have access to Server B")
    
    def test_user_a_cannot_whitelist_on_server_b(self):
        """Test that User A (Group A) cannot whitelist on Server B (Group B)"""
        self.client.login(username='userA', password='pass123')
        response = self.client.post(reverse('whitelist_add', args=[self.server_b.id]), {
            'minecraft_username': 'TestPlayer'
        })
        
        self.assertEqual(response.status_code, 403,
                        "User A should not be able to whitelist on Server B")
    
    def test_user_b_can_access_server_b(self):
        """Test that User B (Group B) CAN access Server B (Group B)"""
        self.client.login(username='userB', password='pass123')
        
        with patch('servers.views.RconHandler') as mock_handler_class:
            mock_handler = MagicMock()
            mock_handler.get_players.return_value = {
                'success': True,
                'players': [],
                'message': 'No players online'
            }
            mock_handler_class.return_value = mock_handler
            
            response = self.client.get(reverse('player_list', args=[self.server_b.id]))
            
            self.assertEqual(response.status_code, 200,
                            "User B should have access to Server B")
