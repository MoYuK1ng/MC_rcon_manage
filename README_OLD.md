# IronGate - Minecraft RCON Web Portal

A Django-based web portal for managing Minecraft server whitelists and monitoring online players through RCON protocol.

## Features

- 🔐 **Secure Authentication** - User login with group-based access control
- 🎮 **Server Management** - View and manage multiple Minecraft servers
- 👥 **Player Monitoring** - Real-time player list with auto-refresh (30s polling)
- ✅ **Whitelist Management** - Add players to server whitelists via RCON
- 🔒 **Encrypted Credentials** - RCON passwords encrypted with Fernet
- 🌍 **Internationalization** - English and Simplified Chinese support
- 📱 **Responsive Design** - Bootstrap 5 UI works on all devices
- ⚡ **HTMX Integration** - Dynamic updates without page reloads

## Technology Stack

- **Backend**: Django 5.0
- **Database**: SQLite (dev) / PostgreSQL (production-ready)
- **RCON Client**: mcrcon
- **Security**: cryptography (Fernet encryption)
- **Frontend**: Bootstrap 5 + HTMX
- **Testing**: pytest + Hypothesis (property-based testing)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Encryption Key

```bash
python generate_key.py
```

This creates a `.env` file with your RCON encryption key.

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000/admin to configure servers and groups.

## Configuration

### Adding Servers

1. Log in to Django admin at `/admin/`
2. Create Groups (e.g., "SMP Players", "Creative Players")
3. Add Users and assign them to Groups
4. Create Servers:
   - Name: Display name
   - IP Address: Server IPv4
   - RCON Port: Default 25575
   - RCON Password: Will be encrypted automatically
   - Groups: Select which groups can access this server

### Group-Based Access Control

- Users only see servers linked to their groups
- Superusers see all servers
- Access is checked for all RCON operations

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest servers/tests/

# Specific test categories
pytest servers/tests/test_models.py      # Model tests
pytest servers/tests/test_services.py    # RCON service tests
pytest servers/tests/test_views.py       # View tests
pytest servers/tests/test_properties.py  # Property-based tests
```

**Test Coverage**: 70 tests (12 property-based, 58 unit tests)

## Security Features

### Password Encryption
- RCON passwords encrypted with Fernet symmetric encryption
- Encryption key stored in environment variables
- Never stored in plaintext or hashed

### Input Validation
- Minecraft usernames validated with regex: `^[a-zA-Z0-9_]{3,16}$`
- Prevents command injection attacks
- Validation occurs before RCON transmission

### Access Control
- `@login_required` on all protected views
- `@user_has_server_access` decorator for group-based authorization
- 403 Forbidden for unauthorized access attempts

## Project Structure

```
irongate/
├── irongate/           # Django project settings
├── servers/            # Main application
│   ├── models.py       # Server & WhitelistRequest models
│   ├── views.py        # Dashboard, PlayerList, WhitelistAdd views
│   ├── decorators.py   # Access control decorators
│   ├── services/       # RCON service layer
│   ├── utils/          # Encryption utilities
│   ├── templates/      # HTML templates
│   └── tests/          # Comprehensive test suite
├── locale/             # Translation files (i18n)
├── .env                # Environment variables (not in git)
└── requirements.txt    # Python dependencies
```

## API Endpoints

- `GET /dashboard/` - Main dashboard (shows accessible servers)
- `GET /server/<id>/players/` - HTMX endpoint for player list
- `POST /server/<id>/whitelist/` - Add player to whitelist
- `POST /i18n/setlang/` - Language switcher

## Internationalization

The application supports English and Simplified Chinese.

To compile translations (requires gettext):
```bash
python manage.py compilemessages
```

See `locale/README.md` for detailed instructions.

## Development

### Running Tests
```bash
pytest servers/tests/ -v
```

### Code Quality
- Property-based testing with Hypothesis
- Comprehensive unit tests with mocking
- Django TestCase for integration tests

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in settings
2. Generate a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Enable HTTPS and set security headers
6. Run `python manage.py check --deploy`

## License

Copyright © 2024 IronGate

## Support

For issues or questions, contact your system administrator.
