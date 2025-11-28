"""
RCON Manager Service for IronGate
Handles RCON connections and command execution for Minecraft servers
"""

import re
import socket
from contextlib import contextmanager
from typing import Dict, List
from mcrcon import MCRcon, MCRconException


class RconHandler:
    """
    Handles RCON connections and command execution for a Minecraft server.
    
    Uses context managers to ensure connections are properly closed.
    Provides methods for getting player lists and managing whitelists.
    """
    
    def __init__(self, server):
        """
        Initialize the RCON handler for a specific server.
        
        Args:
            server: Server model instance with RCON credentials
        """
        self.server = server
        self.host = str(server.ip_address)
        self.port = server.rcon_port
        self.password = server.get_password()
    
    @contextmanager
    def _connect(self):
        """
        Context manager for RCON connections.
        
        Ensures connections are properly closed even if errors occur.
        
        Yields:
            MCRcon: Connected RCON client
        
        Raises:
            socket.timeout: If connection times out
            ConnectionRefusedError: If server refuses connection
            MCRconException: If RCON authentication fails or other RCON errors occur
        """
        rcon = None
        try:
            rcon = MCRcon(self.host, self.password, port=self.port, timeout=5)
            rcon.connect()
            yield rcon
        except socket.timeout:
            raise socket.timeout(f"Connection to {self.host}:{self.port} timed out")
        except ConnectionRefusedError:
            raise ConnectionRefusedError(f"Connection to {self.host}:{self.port} refused")
        except MCRconException as e:
            raise MCRconException(f"RCON error: {str(e)}")
        finally:
            if rcon:
                try:
                    rcon.disconnect()
                except Exception:
                    # Ignore errors during disconnect
                    pass
    
    def _parse_player_list(self, response: str) -> List[str]:
        """
        Parse player names from RCON 'list' command response.
        
        Handles various response formats:
        - "There are 3/20 players online: Steve, Alex, Notch"
        - "There are 0/20 players online"
        - "There are 0 of a max of 20 players online:"
        
        Args:
            response: Raw RCON response string
        
        Returns:
            List[str]: List of player usernames (empty if no players online)
        """
        if not response:
            return []
        
        # Pattern 1: "There are X/Y players online: Player1, Player2, Player3"
        # Pattern 2: "There are X of a max of Y players online: Player1, Player2"
        match = re.search(r'There are (\d+)(?:/| of a max of )(\d+) players online:?\s*(.*)', response, re.IGNORECASE)
        
        if match:
            player_count = int(match.group(1))
            player_names_str = match.group(3).strip()
            
            # If no players online
            if player_count == 0 or not player_names_str:
                return []
            
            # Split by comma and strip whitespace
            players = [name.strip() for name in player_names_str.split(',') if name.strip()]
            return players
        
        # If pattern doesn't match, return empty list
        return []
    
    def get_players(self) -> Dict[str, any]:
        """
        Get the list of online players from the server.
        
        Executes the 'list' command via RCON and parses the response.
        
        Returns:
            dict: {
                'success': bool,
                'players': List[str],  # List of player usernames
                'message': str         # Success message or error description
            }
        """
        try:
            with self._connect() as rcon:
                response = rcon.command('list')
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
        
        Executes the 'whitelist add <username>' command via RCON.
        
        Args:
            username: Minecraft username to whitelist
        
        Returns:
            dict: {
                'success': bool,
                'message': str  # Server response or error description
            }
        """
        try:
            with self._connect() as rcon:
                response = rcon.command(f'whitelist add {username}')
                
                return {
                    'success': True,
                    'message': response if response else f'Added {username} to whitelist'
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
