"""
Unit Tests for RCON Service
Tests RconHandler with mocked RCON connections
"""

import pytest
import socket
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
from mcrcon import MCRconException

from servers.models import Server
from servers.services.rcon_manager import RconHandler


@pytest.mark.unit
class TestRconHandlerConnection(TestCase):
    """Unit tests for RCON connection management"""
    
    def setUp(self):
        """Set up test server"""
        self.server = Server(
            name='Test Server',
            ip_address='192.168.1.100',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.save()
        
        self.handler = RconHandler(self.server)
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_connection_context_manager_connects_and_disconnects(self, mock_rcon_class):
        """Test that context manager properly connects and disconnects"""
        mock_rcon = MagicMock()
        mock_rcon_class.return_value = mock_rcon
        
        with self.handler._connect() as rcon:
            self.assertEqual(rcon, mock_rcon)
            mock_rcon.connect.assert_called_once()
        
        # After exiting context, disconnect should be called
        mock_rcon.disconnect.assert_called_once()
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_connection_disconnects_even_on_error(self, mock_rcon_class):
        """Test that disconnect is called even if an error occurs"""
        mock_rcon = MagicMock()
        mock_rcon.command.side_effect = Exception("Test error")
        mock_rcon_class.return_value = mock_rcon
        
        try:
            with self.handler._connect() as rcon:
                rcon.command('test')
        except Exception:
            pass
        
        # Disconnect should still be called
        mock_rcon.disconnect.assert_called_once()
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_connection_timeout_raises_error(self, mock_rcon_class):
        """Test that connection timeout raises socket.timeout"""
        mock_rcon_class.side_effect = socket.timeout("Connection timed out")
        
        with self.assertRaises(socket.timeout):
            with self.handler._connect():
                pass
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_connection_refused_raises_error(self, mock_rcon_class):
        """Test that connection refused raises ConnectionRefusedError"""
        mock_rcon_class.side_effect = ConnectionRefusedError("Connection refused")
        
        with self.assertRaises(ConnectionRefusedError):
            with self.handler._connect():
                pass
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_rcon_authentication_failure_raises_error(self, mock_rcon_class):
        """Test that RCON authentication failure raises MCRconException"""
        mock_rcon_class.side_effect = MCRconException("Authentication failed")
        
        with self.assertRaises(MCRconException):
            with self.handler._connect():
                pass


@pytest.mark.unit
class TestRconHandlerGetPlayers(TestCase):
    """Unit tests for get_players method"""
    
    def setUp(self):
        """Set up test server"""
        self.server = Server(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.save()
        
        self.handler = RconHandler(self.server)
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_get_players_with_players_online(self, mock_rcon_class):
        """Test getting player list when players are online"""
        mock_rcon = MagicMock()
        mock_rcon.command.return_value = "There are 3/20 players online: Steve, Alex, Notch"
        mock_rcon_class.return_value = mock_rcon
        
        result = self.handler.get_players()
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['players']), 3)
        self.assertIn('Steve', result['players'])
        self.assertIn('Alex', result['players'])
        self.assertIn('Notch', result['players'])
        self.assertIn('3 player(s)', result['message'])
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_get_players_with_no_players_online(self, mock_rcon_class):
        """Test getting player list when server is empty"""
        mock_rcon = MagicMock()
        mock_rcon.command.return_value = "There are 0/20 players online"
        mock_rcon_class.return_value = mock_rcon
        
        result = self.handler.get_players()
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['players']), 0)
        self.assertEqual(result['players'], [])
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_get_players_handles_timeout(self, mock_rcon_class):
        """Test that get_players handles connection timeout gracefully"""
        mock_rcon_class.side_effect = socket.timeout("Connection timed out")
        
        result = self.handler.get_players()
        
        self.assertFalse(result['success'])
        self.assertEqual(result['players'], [])
        self.assertIn('timed out', result['message'].lower())
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_get_players_handles_connection_refused(self, mock_rcon_class):
        """Test that get_players handles connection refused gracefully"""
        mock_rcon_class.side_effect = ConnectionRefusedError("Connection refused")
        
        result = self.handler.get_players()
        
        self.assertFalse(result['success'])
        self.assertEqual(result['players'], [])
        self.assertIn('refused', result['message'].lower())
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_get_players_handles_rcon_exception(self, mock_rcon_class):
        """Test that get_players handles RCON exceptions gracefully"""
        mock_rcon_class.side_effect = MCRconException("Authentication failed")
        
        result = self.handler.get_players()
        
        self.assertFalse(result['success'])
        self.assertEqual(result['players'], [])
        self.assertIn('RCON error', result['message'])


@pytest.mark.unit
class TestRconHandlerAddWhitelist(TestCase):
    """Unit tests for add_whitelist method"""
    
    def setUp(self):
        """Set up test server"""
        self.server = Server(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.save()
        
        self.handler = RconHandler(self.server)
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_add_whitelist_success(self, mock_rcon_class):
        """Test successfully adding a player to whitelist"""
        mock_rcon = MagicMock()
        mock_rcon.command.return_value = "Added TestPlayer to the whitelist"
        mock_rcon_class.return_value = mock_rcon
        
        result = self.handler.add_whitelist('TestPlayer')
        
        self.assertTrue(result['success'])
        self.assertIn('TestPlayer', result['message'])
        
        # Verify the correct command was sent
        mock_rcon.command.assert_called_once_with('whitelist add TestPlayer')
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_add_whitelist_handles_timeout(self, mock_rcon_class):
        """Test that add_whitelist handles connection timeout gracefully"""
        mock_rcon_class.side_effect = socket.timeout("Connection timed out")
        
        result = self.handler.add_whitelist('TestPlayer')
        
        self.assertFalse(result['success'])
        self.assertIn('timed out', result['message'].lower())
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_add_whitelist_handles_connection_refused(self, mock_rcon_class):
        """Test that add_whitelist handles connection refused gracefully"""
        mock_rcon_class.side_effect = ConnectionRefusedError("Connection refused")
        
        result = self.handler.add_whitelist('TestPlayer')
        
        self.assertFalse(result['success'])
        self.assertIn('refused', result['message'].lower())
    
    @patch('servers.services.rcon_manager.MCRcon')
    def test_add_whitelist_handles_rcon_exception(self, mock_rcon_class):
        """Test that add_whitelist handles RCON exceptions gracefully"""
        mock_rcon_class.side_effect = MCRconException("Authentication failed")
        
        result = self.handler.add_whitelist('TestPlayer')
        
        self.assertFalse(result['success'])
        self.assertIn('RCON error', result['message'])


@pytest.mark.unit
class TestRconHandlerParser(TestCase):
    """Unit tests for RCON response parser"""
    
    def setUp(self):
        """Set up test server"""
        self.server = Server(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.save()
        
        self.handler = RconHandler(self.server)
    
    def test_parse_standard_format_with_players(self):
        """Test parsing standard format: 'There are X/Y players online: ...'"""
        response = "There are 3/20 players online: Steve, Alex, Notch"
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(len(players), 3)
        self.assertEqual(players, ['Steve', 'Alex', 'Notch'])
    
    def test_parse_standard_format_no_players(self):
        """Test parsing when no players are online"""
        response = "There are 0/20 players online"
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(len(players), 0)
        self.assertEqual(players, [])
    
    def test_parse_alternative_format(self):
        """Test parsing alternative format: 'There are X of a max of Y players online:'"""
        response = "There are 2 of a max of 20 players online: Player1, Player2"
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(len(players), 2)
        self.assertEqual(players, ['Player1', 'Player2'])
    
    def test_parse_with_extra_whitespace(self):
        """Test parsing handles extra whitespace around player names"""
        response = "There are 2/20 players online:  Steve  ,  Alex  "
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(len(players), 2)
        self.assertEqual(players, ['Steve', 'Alex'])
    
    def test_parse_empty_response(self):
        """Test parsing empty or None response"""
        self.assertEqual(self.handler._parse_player_list(""), [])
        self.assertEqual(self.handler._parse_player_list(None), [])
    
    def test_parse_malformed_response(self):
        """Test parsing malformed response returns empty list"""
        response = "Some random text that doesn't match the pattern"
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(players, [])
    
    def test_parse_single_player(self):
        """Test parsing with a single player online"""
        response = "There are 1/20 players online: Steve"
        players = self.handler._parse_player_list(response)
        
        self.assertEqual(len(players), 1)
        self.assertEqual(players, ['Steve'])
