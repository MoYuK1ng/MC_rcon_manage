#!/bin/bash
# IronGate Development Server Launcher for Linux/Mac
# Usage: ./run.sh [port|random]

if [ -z "$1" ]; then
    python run_server.py
elif [ "$1" = "random" ]; then
    python run_server.py --random
else
    python run_server.py -p "$1"
fi
