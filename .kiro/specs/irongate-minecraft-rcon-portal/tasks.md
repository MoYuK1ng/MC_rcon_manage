# Implementation Plan

- [x] 1. Phase 1: Environment & Core Setup



  - Initialize Django project structure and configure environment
  - _Requirements: 1.3, 9.1, 9.5_

- [x] 1.1 Create requirements.txt with all dependencies


  - Include: django>=5.0, mcrcon, cryptography, python-dotenv, django-htmx, hypothesis, pytest-django
  - _Requirements: 1.1, 9.1_

- [x] 1.2 Create Django project and servers app


  - Run `django-admin startproject irongate`
  - Run `python manage.py startapp servers`
  - _Requirements: All_

- [x] 1.3 Create Fernet key generation helper script


  - Create `generate_key.py` in project root
  - Script should generate a Fernet key and display instructions for .env file
  - _Requirements: 1.3_

- [x] 1.4 Configure Django settings for i18n and environment variables


  - Set `USE_I18N = True`, `USE_L10N = True`
  - Configure `LANGUAGES = [('en', 'English'), ('zh-hans', 'Simplified Chinese')]`
  - Set `LOCALE_PATHS` for translation files
  - Load `RCON_ENCRYPTION_KEY` from environment using python-dotenv
  - Add `django.middleware.locale.LocaleMiddleware` to MIDDLEWARE
  - Configure `django_htmx` in INSTALLED_APPS
  - _Requirements: 1.3, 9.1, 9.5_

- [x] 2. Phase 2: Models & Security Layer



  - Implement data models with encryption and validation
  - _Requirements: 1.1, 1.2, 1.4, 5.1, 5.2, 8.1_

- [x] 2.1 Implement encryption utility


  - Create `servers/utils/encryption.py`
  - Implement `EncryptionUtility` class with Fernet encryption/decryption
  - Load encryption key from environment variable
  - _Requirements: 1.1, 1.2, 1.5_

- [x] 2.2 Write property test for encryption round-trip


  - **Property 1: Password encryption round-trip**
  - **Validates: Requirements 1.1, 1.2**

- [x] 2.3 Implement Server model



  - Create Server model in `servers/models.py`
  - Fields: name, ip_address, rcon_port, rcon_password_encrypted, groups (ManyToMany), timestamps
  - Implement `set_password()` and `get_password()` methods using EncryptionUtility
  - Use `gettext_lazy` for all field verbose names
  - _Requirements: 1.1, 1.2, 1.4, 2.1, 9.4_

- [x] 2.4 Write property test for encrypted password storage


  - **Property 2: Encrypted passwords are never plaintext**
  - **Validates: Requirements 1.4**

- [x] 2.5 Implement WhitelistRequest model


  - Create WhitelistRequest model in `servers/models.py`
  - Fields: user (FK), server (FK), minecraft_username, status, response_log, created_at
  - Add regex validator for minecraft_username: `^[a-zA-Z0-9_]{3,16}$`
  - Use `gettext_lazy` for field verbose names and status choices
  - _Requirements: 5.1, 5.2, 8.1, 9.4_

- [x] 2.6 Write property test for username validation


  - **Property 12: Invalid username is rejected**
  - **Validates: Requirements 5.2, 8.1, 8.2, 8.3, 8.4**

- [x] 2.7 Create and run database migrations

  - Run `python manage.py makemigrations`
  - Run `python manage.py migrate`
  - _Requirements: All model requirements_

- [x] 2.8 Register models in Django admin


  - Create `servers/admin.py`
  - Register Server and WhitelistRequest models
  - Configure admin display fields and filters
  - Ensure password field shows as encrypted in admin
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2.9 Write unit tests for models


  - Test Server password encryption/decryption methods
  - Test WhitelistRequest creation and validation
  - Test model string representations
  - _Requirements: 1.1, 1.2, 1.4, 5.1, 5.2, 8.1_

- [x] 3. Phase 3: RCON Service Layer


  - Implement RCON connection and command execution
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 7.1, 7.2, 7.3, 7.4_

- [x] 3.1 Implement RconHandler service class


  - Create `servers/services/rcon_manager.py`
  - Implement `RconHandler` class with `__init__(server)`
  - Implement `_connect()` context manager with error handling
  - Handle timeout, connection refused, and authentication errors
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 3.2 Implement get_players method

  - Add `get_players()` method to RconHandler
  - Send "list" command via RCON
  - Parse response to extract player usernames (handle various formats)
  - Return structured dict: `{'success': bool, 'players': list, 'message': str}`
  - _Requirements: 4.1, 4.2, 4.3, 7.4_

- [x] 3.3 Write property test for RCON response parsing


  - **Property 9: RCON response parsing extracts players**
  - **Validates: Requirements 4.3**

- [x] 3.4 Implement add_whitelist method

  - Add `add_whitelist(username)` method to RconHandler
  - Send "whitelist add <username>" command via RCON
  - Return structured dict: `{'success': bool, 'message': str}`
  - _Requirements: 5.1, 7.4_

- [x] 3.5 Write property test for RCON handler return structure


  - **Property 16: RCON handler returns structured response**
  - **Validates: Requirements 7.4**

- [x] 3.6 Write unit tests for RconHandler


  - Test connection context manager
  - Test get_players with mocked RCON
  - Test add_whitelist with mocked RCON
  - Test error handling for connection failures
  - _Requirements: 4.1, 4.2, 5.1, 7.1, 7.2, 7.3_

- [x] 4. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Phase 4: Views, URLs & Access Control


  - Implement views with authentication and group-based access control
  - _Requirements: 2.2, 2.3, 2.4, 3.1, 3.3, 3.4, 4.1, 4.5, 5.1, 5.3, 5.4, 5.5_



- [ ] 5.1 Create access control decorator
  - Create `servers/decorators.py`
  - Implement `@user_has_server_access` decorator
  - Check if user's groups have access to requested server
  - Return 403 Forbidden if access denied


  - _Requirements: 2.2, 2.4, 4.5, 5.5_

- [ ] 5.2 Write property tests for access control
  - **Property 3: Group membership grants server access**


  - **Property 4: Group removal revokes exclusive server access**
  - **Property 5: Multiple group membership provides union of server access**
  - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 5.3 Implement DashboardView
  - Create `servers/views.py`

  - Implement DashboardView (class-based view)
  - Use `@login_required` decorator
  - Query servers: `Server.objects.filter(groups__in=request.user.groups.all()).distinct()`
  - Pass server list to template context

  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 5.4 Write property tests for dashboard filtering
  - **Property 6: Dashboard displays only accessible servers**
  - **Property 7: Server deduplication in dashboard**
  - **Validates: Requirements 3.1, 3.3**


- [ ] 5.5 Implement PlayerListView
  - Create PlayerListView in `servers/views.py`
  - Use `@login_required` and `@user_has_server_access` decorators
  - Call `RconHandler(server).get_players()`

  - Return HTML fragment for HTMX (player list)
  - Handle RCON errors gracefully
  - _Requirements: 4.1, 4.2, 4.5_

- [ ] 5.6 Write property test for player list access control
  - **Property 8: Player list triggers RCON command**
  - **Property 10: Unauthorized player list access is denied**
  - **Validates: Requirements 4.1, 4.5**

- [x] 5.7 Implement WhitelistAddView

  - Create WhitelistAddView in `servers/views.py`
  - Use `@login_required` and `@user_has_server_access` decorators
  - Validate minecraft_username before processing
  - Create WhitelistRequest record
  - Call `RconHandler(server).add_whitelist(username)`
  - Update WhitelistRequest status based on RCON result (PROCESSED or FAILED)
  - Store response in response_log


  - Return redirect with flash message
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.5_

- [ ] 5.8 Write property tests for whitelist functionality
  - **Property 11: Valid username creates whitelist request**
  - **Property 13: Successful RCON updates status to PROCESSED**


  - **Property 14: Failed RCON updates status to FAILED**
  - **Property 15: Unauthorized whitelist access is denied**
  - **Property 17: Username validation occurs before RCON transmission**
  - **Validates: Requirements 5.1, 5.3, 5.4, 5.5, 8.5**






- [ ] 5.9 Configure URL patterns
  - Create `servers/urls.py` with app URL patterns


  - Update `irongate/urls.py` with main URL configuration
  - Include Django auth URLs for login/logout
  - Include i18n URLs for language switching
  - Add URL patterns for dashboard, player_list, whitelist_add
  - _Requirements: All view requirements_

- [ ] 5.10 Write unit tests for views
  - Test DashboardView with authenticated/unauthenticated users


  - Test PlayerListView with HTMX requests
  - Test WhitelistAddView with valid/invalid data
  - Test access control across all views
  - _Requirements: 3.1, 3.4, 4.1, 4.5, 5.1, 5.5_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.



- [ ] 7. Phase 5: Templates & Frontend
  - Create responsive UI with Bootstrap 5, HTMX, and i18n support
  - _Requirements: 9.1, 9.2, 9.3, 10.1, 10.2, 10.3, 10.4_

- [ ] 7.1 Create base template with Bootstrap and HTMX
  - Create `servers/templates/base.html`


  - Include Bootstrap 5 CDN
  - Include HTMX CDN
  - Add CSRF token configuration for HTMX requests
  - Create navigation bar with login/logout links
  - Add language switcher form in navbar

  - Use `{% trans %}` tags for all text
  - _Requirements: 9.2, 9.3, 10.1, 10.4_

- [ ] 7.2 Create dashboard template
  - Create `servers/templates/dashboard.html`


  - Extend base.html
  - Display server cards in responsive grid (Bootstrap grid system)
  - Each card shows server name, IP, port
  - Include player list section with HTMX polling
  - Include whitelist form

  - Use `{% trans %}` tags for all text
  - _Requirements: 3.1, 3.2, 3.3, 9.3, 10.1, 10.2, 10.3_

- [x] 7.3 Create player list fragment template



  - Create `servers/templates/includes/player_list.html`
  - Display list of online players
  - Show "No players online" message when empty
  - Show error message when RCON fails
  - Use `{% trans %}` tags for all text
  - _Requirements: 4.1, 4.2, 4.3, 9.3_

- [ ] 7.4 Create login template
  - Create `servers/templates/registration/login.html`
  - Extend base.html
  - Create login form with Bootstrap styling
  - Use `{% trans %}` tags for all text
  - _Requirements: 3.4, 9.3, 10.1_

- [ ] 7.5 Configure HTMX for player list auto-refresh
  - Add `hx-get` attribute to player list container
  - Set `hx-trigger="load, every 30s"` for automatic polling
  - Configure `hx-target` and `hx-swap` for seamless updates
  - _Requirements: 4.4, 10.4_

- [ ] 7.6 Create translation files
  - Create locale directory structure: `locale/zh_hans/LC_MESSAGES/`
  - Run `python manage.py makemessages -l zh_hans`
  - Translate all strings in generated `django.po` file to Simplified Chinese
  - Run `python manage.py compilemessages`
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 7.7 Add static files configuration
  - Configure STATIC_URL and STATIC_ROOT in settings.py
  - Create static directory for custom CSS if needed
  - Run `python manage.py collectstatic`
  - _Requirements: 10.1_

- [ ] 8. Final Checkpoint - Integration Testing
  - Ensure all tests pass, ask the user if questions arise.
