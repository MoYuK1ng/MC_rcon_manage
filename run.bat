@echo off
REM IronGate Development Server Launcher for Windows
REM Usage: run.bat [port]

if "%1"=="" (
    python run_server.py
) else if "%1"=="random" (
    python run_server.py --random
) else (
    python run_server.py -p %1
)
