# Design Document

## Overview

IronGate is a Django 5.x web application that provides secure, group-based access control for managing Minecraft servers via RCON protocol. The system architecture follows Django's MVT (Model-View-Template) pattern with a service layer for RCON operations. The application uses Fernet symmetric encryption for credential storage, implements comprehensive input validation to prevent command injection, and supports internationalization (i18n) for English and Simplified Chinese languages.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│              (Bootstrap 5 + HTMX for AJAX)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Views      │  │  Templates   │  │    Models    │     │
│  │  (Auth +     │◄─┤  (i18n +     │  │  (Server,    │     │
│  │   Access     │  │   Bootstrap) │  │   Whitelist) │     │
│  │   Control)   │  └──────────────┘  └──────┬───────┘     │
│  └──────┬───────┘                            │              │
│         │                                    │              │
│         ▼                                    ▼              │
│  ┌──────────────────────┐         ┌──────────────────┐    │
│  │   RconHandler        │         │  Encryption      │    │
│  │   Service            │         │  Utility         │    │
│  │  (mcrcon wrapper)    │         │  (Fernet)        │    │
│  └──────┬───────────────┘         └──────────────────┘    │
└─────────┼──────────────────────────────────────────────────┘
          │ RCON Protocol
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minecraft Servers (RCON enabled)                │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

1. **Presentation Layer (Templates + HTMX)**
   - Renders UI using Django templates with Bootstrap 5
   - Handles real-time updates via HTMX polling
   - Supports language switching through i18n

2. **Application Layer (Views)**
   - Authenticates users and enforces group-based access control
   - Validates input data (especially Minecraft usernames)
   - Coordinates between models and services
   - Returns HTML responses or fragments

3. **Service Layer (RconHandler)**
   - Manages RCON connections with context managers
   - Executes commands and parses responses
   - Handles connection errors and timeouts gracefully

4. **Data Layer (Models)**
   - Stores server configurations with encrypted passwords
   - Tracks whitelist requests and their statuses
   - Manages user-group-server relationships

5. **Security Layer (Encryption Utility)**
   - Encrypts/decrypts RCON passwords using Fernet
   - Loads encryption key from environment variables

## Components and Interfaces

### 1. Models (servers/models.py)

#### Server Model

```python
class Server(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    rcon_port = models.IntegerField(default=25575)
    rcon_password_encrypted = models.BinaryField()
    groups = models.ManyToManyField('auth.Group', related_name='servers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_password(self, raw_password: str) -> None
    def get_password(self) -> str
    def __str__(self) -> str
```

**Relationships:**
- ManyToMany with Django's `auth.Group` model
- OneToMany with `WhitelistRequest` model (reverse relation)

#### WhitelistRequest Model

```python
class WhitelistRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    minecraft_username = models.CharField(max_length=16, validators=[...])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    response_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str
```

**Relationships:**
- ManyToOne with `auth.User`
- ManyToOne with `Server`

### 2. Encryption Utility (servers/utils/encryption.py)

```python
class EncryptionUtility:
    def __init__(self):
        # Load RCON_ENCRYPTION_KEY from environment
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, plaintext: str) -> bytes
    def decrypt(self, ciphertext: bytes) -> str
```

**Interface:**
- `encrypt(plaintext: str) -> bytes`: Takes plaintext password, returns encrypted bytes
- `decrypt(ciphertext: bytes) -> str`: Takes encrypted bytes, returns plaintext password

### 3. RCON Service (servers/services/rcon_manager.py)

```python
class RconHandler:
    def __init__(self, server: Server):
        self.server = server
        self.host = server.ip_address
        self.port = server.rcon_port
        self.password = server.get_password()
    
    @contextmanager
    def _connect(self) -> MCRcon
    
    def get_players(self) -> dict
        # Returns: {'success': bool, 'players': list[str], 'message': str}
    
    def add_whitelist(self, username: str) -> dict
        # Returns: {'success': bool, 'message': str}
```

**Interface:**
- `get_players()`: Executes "list" command, parses player names
- `add_whitelist(username)`: Executes "whitelist add <username>"
- Both methods return structured dictionaries with success status and messages

### 4. Views (servers/views.py)

#### DashboardView
- **URL:** `/dashboard/`
- **Method:** GET
- **Auth:** Required
- **Logic:** Queries servers accessible to user's groups
- **Returns:** HTML page with server cards

#### PlayerListView
- **URL:** `/server/<int:server_id>/players/`
- **Method:** GET
- **Auth:** Required + Group Access Check
- **Logic:** Calls RconHandler.get_players()
- **Returns:** HTML fragment (for HTMX)

#### WhitelistAddView
- **URL:** `/server/<int:server_id>/whitelist/`
- **Method:** POST
- **Auth:** Required + Group Access Check
- **Logic:** Validates username, creates WhitelistRequest, calls RconHandler.add_whitelist()
- **Returns:** Redirect with flash message

#### LanguageSwitchView
- **URL:** `/i18n/setlang/`
- **Method:** POST
- **Auth:** Not required
- **Logic:** Uses Django's set_language view
- **Returns:** Redirect to previous page

### 5. URL Configuration

```python
# irongate/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('server/<int:server_id>/players/', PlayerListView.as_view(), name='player_list'),
    path('server/<int:server_id>/whitelist/', WhitelistAddView.as_view(), name='whitelist_add'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),
]
```

## Data Models

### Entity-Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   auth.User     │         │   auth.Group    │
│─────────────────│         │─────────────────│
│ id (PK)         │         │ id (PK)         │
│ username        │◄───┐    │ name            │
│ email           │    │    └────────┬────────┘
│ password        │    │             │
└─────────────────┘    │             │ ManyToMany
                       │             │
                       │    ┌────────▼────────┐
                       │    │     Server      │
                       │    │─────────────────│
                       │    │ id (PK)         │
                       │    │ name            │
                       │    │ ip_address      │
                       │    │ rcon_port       │
                       │    │ rcon_password_  │
                       │    │   encrypted     │
                       │    │ created_at      │
                       │    │ updated_at      │
                       │    └────────┬────────┘
                       │             │
                       │             │ ForeignKey
                       │             │
                  FK   │    ┌────────▼────────────┐
                  ┌────┴────┤ WhitelistRequest    │
                  │         │─────────────────────│
                  │         │ id (PK)             │
                  │         │ user_id (FK)        │
                  │         │ server_id (FK)      │
                  │         │ minecraft_username  │
                  │         │ status              │
                  │         │ response_log        │
                  │         │ created_at          │
                  └─────────┤                     │
                            └─────────────────────┘
```

### Data Validation Rules

1. **Server.ip_address**: Must be valid IPv4 format
2. **Server.rcon_port**: Integer, typically 25575
3. **Server.rcon_password_encrypted**: Binary field, never null
4. **WhitelistRequest.minecraft_username**: 
   - Regex: `^[a-zA-Z0-9_]{3,16}$`
   - Min length: 3
   - Max length: 16
   - Allowed characters: alphanumeric and underscore only
5. **WhitelistRequest.status**: Must be one of: PENDING, APPROVED, PROCESSED, FAILED

## Corr
ectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Password encryption round-trip

*For any* RCON password string, encrypting it and then decrypting the result should produce the original password value.

**Validates: Requirements 1.1, 1.2**

### Property 2: Encrypted passwords are never plaintext

*For any* Server instance with a password, the value stored in the rcon_password_encrypted field should be binary encrypted data, not the plaintext password string.

**Validates: Requirements 1.4**

### Property 3: Group membership grants server access

*For any* User, Group, and set of Servers, when the User is added to the Group and the Servers are linked to that Group, the User should have access to all those Servers.

**Validates: Requirements 2.2**

### Property 4: Group removal revokes exclusive server access

*For any* User belonging to multiple Groups, removing the User from one Group should revoke access only to Servers that are exclusively linked to that removed Group and not to any of the User's remaining Groups.

**Validates: Requirements 2.3**

### Property 5: Multiple group membership provides union of server access

*For any* User belonging to multiple Groups, the set of accessible Servers should equal the union of all Servers linked to any of those Groups.

**Validates: Requirements 2.4**

### Property 6: Dashboard displays only accessible servers

*For any* User, the dashboard query should return exactly the set of Servers that are linked to at least one Group the User belongs to.

**Validates: Requirements 3.1**

### Property 7: Server deduplication in dashboard

*For any* Server linked to multiple Groups that a User belongs to, the dashboard should display that Server exactly once (no duplicates).

**Validates: Requirements 3.3**

### Property 8: Player list triggers RCON command

*For any* Server that a User has access to, requesting the player list should result in the RCON "list" command being sent to that Server.

**Validates: Requirements 4.1**

### Property 9: RCON response parsing extracts players

*For any* valid RCON "list" response string, the parser should correctly extract all player usernames into a structured list.

**Validates: Requirements 4.3**

### Property 10: Unauthorized player list access is denied

*For any* User and Server where the User does not have access (Server not linked to any of User's Groups), attempting to view the player list should be denied with an authorization error.

**Validates: Requirements 4.5**

### Property 11: Valid username creates whitelist request

*For any* valid Minecraft username (matching regex ^[a-zA-Z0-9_]{3,16}$) and accessible Server, submitting a whitelist request should create a WhitelistRequest record and trigger the RCON "whitelist add" command.

**Validates: Requirements 5.1**

### Property 12: Invalid username is rejected

*For any* string that does not match the regex pattern ^[a-zA-Z0-9_]{3,16}$, submitting it as a Minecraft username should be rejected with a validation error before any RCON command is executed.

**Validates: Requirements 5.2, 8.1, 8.2, 8.3, 8.4**

### Property 13: Successful RCON updates status to PROCESSED

*For any* WhitelistRequest where the RCON command succeeds, the status should be updated to PROCESSED and the server response should be stored in response_log.

**Validates: Requirements 5.3**

### Property 14: Failed RCON updates status to FAILED

*For any* WhitelistRequest where the RCON command fails, the status should be updated to FAILED and the error message should be stored in response_log.

**Validates: Requirements 5.4**

### Property 15: Unauthorized whitelist access is denied

*For any* User and Server where the User does not have access, attempting to submit a whitelist request should be denied with an authorization error.

**Validates: Requirements 5.5**

### Property 16: RCON handler returns structured response

*For any* RCON command executed by RconHandler, the return value should be a dictionary containing both a success status boolean and a message string.

**Validates: Requirements 7.4**

### Property 17: Username validation occurs before RCON transmission

*For any* whitelist request, the username validation must complete and pass before the username is sent to the RCON socket.

**Validates: Requirements 8.5**

## Error Handling

### 1. RCON Connection Errors

**Error Types:**
- Connection timeout
- Connection refused
- Authentication failure
- Network unreachable

**Handling Strategy:**
- Use context managers (`with` statement) to ensure connections are always closed
- Catch `socket.timeout`, `ConnectionRefusedError`, and `MCRconException`
- Return structured error responses: `{'success': False, 'message': 'Error description'}`
- Log errors for debugging but display user-friendly messages in UI
- Never expose internal error details (IP addresses, stack traces) to end users

**Example Implementation:**
```python
@contextmanager
def _connect(self):
    rcon = None
    try:
        rcon = MCRcon(self.host, self.password, port=self.port, timeout=5)
        rcon.connect()
        yield rcon
    except socket.timeout:
        raise RconTimeoutError("Server connection timed out")
    except ConnectionRefusedError:
        raise RconConnectionError("Server refused connection")
    except Exception as e:
        raise RconError(f"RCON error: {str(e)}")
    finally:
        if rcon:
            rcon.disconnect()
```

### 2. Input Validation Errors

**Error Types:**
- Invalid Minecraft username format
- Invalid IP address format
- Invalid port number
- Missing required fields

**Handling Strategy:**
- Use Django's built-in validators and custom validators
- Validate at multiple layers: form validation, model validation, view validation
- Return clear, actionable error messages in the user's selected language
- Use regex validation for Minecraft usernames: `^[a-zA-Z0-9_]{3,16}$`
- Prevent SQL injection and command injection through parameterized queries and input sanitization

**Example Validator:**
```python
from django.core.validators import RegexValidator

minecraft_username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,16}$',
    message='Username must be 3-16 characters, alphanumeric and underscores only'
)
```

### 3. Authorization Errors

**Error Types:**
- User not authenticated
- User not in required group
- User attempting to access unauthorized server

**Handling Strategy:**
- Use Django's `@login_required` decorator for authentication
- Implement custom `@user_has_server_access` decorator for group-based authorization
- Return HTTP 403 Forbidden for authorization failures
- Redirect to login page for authentication failures
- Log authorization failures for security auditing

**Example Decorator:**
```python
def user_has_server_access(view_func):
    @wraps(view_func)
    def wrapper(request, server_id, *args, **kwargs):
        server = get_object_or_404(Server, id=server_id)
        if not server.groups.filter(id__in=request.user.groups.all()).exists():
            return HttpResponseForbidden("You do not have access to this server")
        return view_func(request, server_id, *args, **kwargs)
    return wrapper
```

### 4. Encryption Errors

**Error Types:**
- Missing encryption key
- Invalid encryption key format
- Decryption failure (corrupted data)

**Handling Strategy:**
- Validate encryption key exists in environment on application startup
- Fail fast if encryption key is missing or invalid
- Use try-except blocks around encryption/decryption operations
- Log encryption errors but never log plaintext passwords
- Provide clear error messages for administrators

### 5. Database Errors

**Error Types:**
- Integrity constraint violations
- Connection failures
- Transaction rollback

**Handling Strategy:**
- Use Django's transaction management
- Catch `IntegrityError` for duplicate entries or constraint violations
- Use `select_for_update()` for race condition prevention
- Implement proper error messages for constraint violations
- Log database errors for debugging

## Testing Strategy

### Overview

IronGate will use a dual testing approach combining unit tests and property-based tests to ensure comprehensive coverage. Unit tests verify specific examples and integration points, while property-based tests verify universal properties hold across all inputs.

### Property-Based Testing

**Framework:** Hypothesis (Python property-based testing library)

**Configuration:**
- Minimum 100 iterations per property test
- Use `@given` decorator with appropriate strategies
- Tag each test with the property number from this design document

**Test Tagging Format:**
```python
@given(password=st.text(min_size=1, max_size=100))
def test_password_encryption_roundtrip(password):
    """
    Feature: irongate-minecraft-rcon-portal, Property 1: Password encryption round-trip
    """
    # Test implementation
```

**Property Test Coverage:**

1. **Property 1-2: Encryption/Decryption**
   - Generate random password strings
   - Test encryption round-trip
   - Verify encrypted data is not plaintext

2. **Property 3-7: Access Control**
   - Generate random Users, Groups, and Servers
   - Test group membership and server access relationships
   - Verify dashboard filtering and deduplication

3. **Property 8-10: RCON Player List**
   - Generate random RCON response strings
   - Test parser correctness
   - Verify access control for player list endpoint

4. **Property 11-15: Whitelist Management**
   - Generate random usernames (valid and invalid)
   - Test validation logic
   - Verify WhitelistRequest state transitions
   - Test access control for whitelist endpoint

5. **Property 16-17: RCON Handler**
   - Test return value structure
   - Verify validation occurs before RCON transmission

**Strategies for Generators:**
- Use `hypothesis.strategies` for generating test data
- Create custom strategies for Minecraft usernames (valid and invalid)
- Generate realistic RCON response formats
- Use `st.builds()` for creating model instances

**Example Property Test:**
```python
from hypothesis import given, strategies as st
import re

@given(username=st.text(min_size=1, max_size=50))
def test_username_validation(username):
    """
    Feature: irongate-minecraft-rcon-portal, Property 12: Invalid username is rejected
    """
    is_valid = bool(re.match(r'^[a-zA-Z0-9_]{3,16}$', username))
    
    if is_valid:
        # Should not raise validation error
        validator = minecraft_username_validator
        validator(username)  # Should pass
    else:
        # Should raise validation error
        with pytest.raises(ValidationError):
            validator = minecraft_username_validator
            validator(username)
```

### Unit Testing

**Framework:** Django's built-in TestCase (based on unittest)

**Test Coverage:**

1. **Model Tests**
   - Test Server model's `set_password()` and `get_password()` methods
   - Test WhitelistRequest model creation and status transitions
   - Test model string representations

2. **View Tests**
   - Test dashboard view with authenticated and unauthenticated users
   - Test player list view with HTMX requests
   - Test whitelist add view with valid and invalid data
   - Test language switching functionality

3. **Service Tests**
   - Test RconHandler connection management
   - Test RCON command execution with mocked MCRcon
   - Test error handling for connection failures

4. **Integration Tests**
   - Test complete whitelist workflow (form submission → RCON → status update)
   - Test group-based access control across multiple views
   - Test i18n language switching across pages

**Example Unit Test:**
```python
from django.test import TestCase
from django.contrib.auth.models import User, Group
from servers.models import Server

class ServerAccessTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='12345')
        self.group = Group.objects.create(name='TestGroup')
        self.user.groups.add(self.group)
        
        self.server = Server.objects.create(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        self.server.set_password('test_password')
        self.server.groups.add(self.group)
    
    def test_user_can_access_server_in_their_group(self):
        accessible_servers = Server.objects.filter(
            groups__in=self.user.groups.all()
        ).distinct()
        self.assertIn(self.server, accessible_servers)
```

### Test Organization

```
servers/
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Model unit tests
│   ├── test_views.py           # View unit tests
│   ├── test_services.py        # RconHandler unit tests
│   ├── test_properties.py      # Property-based tests
│   └── test_integration.py     # Integration tests
```

### Testing Best Practices

1. **Isolation:** Each test should be independent and not rely on other tests
2. **Fixtures:** Use Django fixtures or factory patterns for test data
3. **Mocking:** Mock external dependencies (RCON connections) in unit tests
4. **Coverage:** Aim for >80% code coverage, 100% for critical security code
5. **CI/CD:** Run all tests automatically on every commit
6. **Performance:** Property tests should complete in reasonable time (<5 minutes total)

### Security Testing

1. **Command Injection Tests**
   - Test username validation with malicious inputs
   - Verify special characters are rejected
   - Test SQL injection attempts

2. **Authentication Tests**
   - Test unauthorized access to all protected endpoints
   - Verify session management
   - Test CSRF protection

3. **Encryption Tests**
   - Verify passwords are never stored in plaintext
   - Test encryption key rotation scenarios
   - Verify encrypted data cannot be decrypted without key

### Manual Testing Checklist

1. **UI/UX Testing**
   - Test responsive layout on mobile and desktop
   - Verify HTMX polling works correctly
   - Test language switching
   - Verify all Chinese translations are correct

2. **RCON Integration Testing**
   - Test with real Minecraft server
   - Verify player list parsing with various server responses
   - Test whitelist commands actually work on server

3. **Admin Interface Testing**
   - Verify all models are registered
   - Test group assignment interface
   - Verify password field is not displayed in plaintext
