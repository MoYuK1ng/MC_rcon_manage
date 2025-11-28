#!/usr/bin/env python
"""
IronGate Development Server Launcher
Allows running Django development server on custom or random ports
"""

import os
import sys
import socket
import random
import argparse
from pathlib import Path


def find_free_port(start_port=8000, max_attempts=100):
    """
    Find a free port starting from start_port.
    
    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try
        
    Returns:
        int: Available port number
        
    Raises:
        RuntimeError: If no free port found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")


def get_random_port(min_port=8000, max_port=9000):
    """
    Get a random available port in the specified range.
    
    Args:
        min_port: Minimum port number
        max_port: Maximum port number
        
    Returns:
        int: Random available port
    """
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        port = random.randint(min_port, max_port)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            attempts += 1
            continue
    
    # Fallback to sequential search
    return find_free_port(min_port)


def is_port_available(port):
    """
    Check if a port is available.
    
    Args:
        port: Port number to check
        
    Returns:
        bool: True if port is available
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description='IronGate Development Server Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                    # Run on default port 8000
  python run_server.py -p 8080            # Run on port 8080
  python run_server.py --random           # Run on random available port
  python run_server.py --host 0.0.0.0     # Listen on all interfaces
  python run_server.py -p 8080 --noreload # Disable auto-reload
        """
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=None,
        help='Port to run the server on (default: 8000 or next available)'
    )
    
    parser.add_argument(
        '--random',
        action='store_true',
        help='Use a random available port between 8000-9000'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)'
    )
    
    parser.add_argument(
        '--noreload',
        action='store_true',
        help='Disable auto-reload (useful for debugging)'
    )
    
    parser.add_argument(
        '--settings',
        type=str,
        default=None,
        help='Django settings module (default: irongate.settings)'
    )
    
    args = parser.parse_args()
    
    # Determine port
    if args.random:
        port = get_random_port()
        print(f"🎲 Using random port: {port}")
    elif args.port:
        if is_port_available(args.port):
            port = args.port
            print(f"✓ Using specified port: {port}")
        else:
            print(f"⚠ Port {args.port} is already in use!")
            port = find_free_port(args.port + 1)
            print(f"→ Using next available port: {port}")
    else:
        # Default behavior: try 8000, then find next available
        if is_port_available(8000):
            port = 8000
            print(f"✓ Using default port: {port}")
        else:
            port = find_free_port(8001)
            print(f"⚠ Port 8000 is in use. Using port: {port}")
    
    # Build Django command
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', args.settings or 'irongate.settings')
    
    # Import Django management
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Build command arguments
    cmd_args = ['manage.py', 'runserver', f'{args.host}:{port}']
    
    if args.noreload:
        cmd_args.append('--noreload')
    
    # Display server info
    print("\n" + "="*60)
    print("🎮 IronGate RCON Portal - Development Server")
    print("="*60)
    print(f"Host:     {args.host}")
    print(f"Port:     {port}")
    print(f"URL:      http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{port}/")
    print(f"Admin:    http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{port}/admin/")
    print(f"Reload:   {'Disabled' if args.noreload else 'Enabled'}")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Django development server
    execute_from_command_line(cmd_args)


if __name__ == '__main__':
    main()
