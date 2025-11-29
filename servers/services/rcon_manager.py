"""
RCON Manager Service for MC RCON Manager
Handles RCON command execution for Minecraft servers using a connection pool.
"""

import re
import socket
from typing import Dict, List
from mcrcon import MCRconException

# Import the global connection pool for persistent connections.
from .rcon_pool import rcon_pool


class RconHandler:
    """
    Handles RCON command execution for a Minecraft server.
    
    This class is a high-level interface that uses a shared RCON connection
    pool for efficiency and performance.
    """
    
    def __init__(self, server):
        """
        Initialize the RCON handler for a specific server.
        
        Args:
            server: Server model instance.
        """
        self.server = server
        self.host = str(server.ip_address)
        self.port = server.rcon_port

    def _execute_command(self, command: str) -> str:
        """
        Retrieves a connection from the pool and executes a command.
        
        Args:
            command: The RCON command string to execute.
        
        Returns:
            The response from the RCON server.
        """
        rcon_client = rcon_pool.get_connection(self.server)
        return rcon_client.command(command)

    def _parse_player_list(self, response: str) -> List[str]:
        """
        Parse player names from RCON 'list' command response.
        
        This implementation is more resilient to format changes than a
        single, strict regex.
        
        Args:
            response: Raw RCON response string.
        
        Returns:
            List of player usernames.
        """
        if not response or 'players online' not in response.lower():
            return []
        
        try:
            # Isolate the part of the string after the colon, where names are listed.
            player_list_str = response.split(':', 1)[1]
        except IndexError:
            # Handles cases like "There are 0 of a max 20 players online:"
            return []
            
        player_names = player_list_str.strip()
        if not player_names:
            return []
            
        # Split by comma and strip whitespace from each name, filtering out empties.
        players = [name.strip() for name in player_names.split(',') if name.strip()]
        return players
    
    def get_players(self) -> Dict[str, any]:
        """
        Get the list of online players from the server.
        
        Returns:
            A dictionary with success status, player list, and a message.
        """
        try:
            response = self._execute_command('list')
            players = self._parse_player_list(response)
            
            return {
                'success': True,
                'players': players,
                'message': f'Found {len(players)} player(s) online'
            }
        
        except socket.timeout:
            return {
                'success': False,
                'players': [],
                'message': f'Connection to {self.host}:{self.port} timed out'
            }
        
        except ConnectionRefusedError:
            return {
                'success': False,
                'players': [],
                'message': f'Connection to {self.host}:{self.port} refused - server may be offline'
            }
        
        except MCRconException as e:
            return {
                'success': False,
                'players': [],
                'message': f'RCON error: {str(e)}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'players': [],
                'message': f'Unexpected error: {str(e)}'
            }
    
    def add_whitelist(self, username: str) -> Dict[str, any]:
        """
        Add a username to the server's whitelist.
        
        Args:
            username: Minecraft username to whitelist.
        
        Returns:
            A dictionary with success status and a server response message.
        """
        # Validate username format to prevent invalid characters.
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
            return {
                'success': False, 
                'message': 'Invalid username format. Must be 3-16 characters, letters, numbers, and underscores.'
            }

        try:
            response = self._execute_command(f'whitelist add {username}')
            
            return {
                'success': True,
                'message': response if response else f'Successfully added {username} to the whitelist.'
            }
        
        except socket.timeout:
            return {
                'success': False,
                'message': f'Connection to {self.host}:{self.port} timed out'
            }
        
        except ConnectionRefusedError:
            return {
                'success': False,
                'message': f'Connection to {self.host}:{self.port} refused - server may be offline'
            }
        
        except MCRconException as e:
            return {
                'success': False,
                'message': f'RCON error: {str(e)}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }
```