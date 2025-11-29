@echo off
echo ========================================
echo   MC RCON Manager - Starting Server
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Running with system Python...
)

echo.
echo Checking system...
python manage.py check

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: System check failed!
    echo Please fix the errors above before starting the server.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Server is starting...
echo ========================================
echo.
echo   Frontend:  http://localhost:8000/
echo   Admin:     http://localhost:8000/admin/
echo   Register:  http://localhost:8000/register/
echo.
echo   Press CTRL+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause
