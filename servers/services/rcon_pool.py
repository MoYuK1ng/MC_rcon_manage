"""
RCON Connection Pool Manager for MC RCON Manager
Provides a thread-safe, persistent store for RCON connections to improve performance.
"""

import threading
from mcrcon import MCRcon, MCRconException

class RconConnectionManager:
    """
    Manages a pool of persistent RCON connections to Minecraft servers.

    This class is thread-safe and designed to be used as a singleton.
    It health-checks connections before returning them and automatically
    reconnects if a connection is dead.
    """
    def __init__(self):
        self._connections: dict = {}
        self._lock = threading.Lock()

    def get_connection(self, server) -> MCRcon:
        """
        Retrieves a valid RCON connection for a given server from the pool.

        If a connection doesn't exist or is no longer valid, a new one
        is created and stored in the pool.

        Args:
            server: The Django Server model instance.

        Returns:
            A connected and authenticated MCRcon instance.
        
        Raises:
            MCRconException: If a new connection fails to establish.
            ConnectionRefusedError: If the server refuses a new connection.
            socket.timeout: If a new connection attempt times out.
        """
        with self._lock:
            conn_key = server.id
            conn = self._connections.get(conn_key)

            try:
                # Health-check the existing connection.
                if conn:
                    conn.command('version')  # A lightweight command to check liveness.
                else:
                    # No connection found in the pool, force creation.
                    raise MCRconException("Connection not found in pool")
            except (MCRconException, BrokenPipeError, ConnectionResetError):
                # If the connection is dead, broken, or non-existent, create a new one.
                conn = MCRcon(
                    host=str(server.ip_address),
                    password=server.get_password(),
                    port=server.rcon_port,
                    timeout=5
                )
                conn.connect()
                self._connections[conn_key] = conn
            
            return conn

# Global instance of the connection manager to be used across the application.
rcon_pool = RconConnectionManager()