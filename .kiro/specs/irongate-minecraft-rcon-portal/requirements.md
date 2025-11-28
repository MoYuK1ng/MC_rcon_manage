# Requirements Document

## Introduction

IronGate is a Django-based web portal that enables authenticated users to manage Minecraft server whitelists and monitor online players through RCON (Remote Console) protocol. The system implements group-based access control, allowing administrators to assign users to groups and link those groups to specific Minecraft servers. Users can only interact with servers their groups have access to, ensuring secure and organized multi-server management.

## Glossary

- **IronGate**: The Django web portal system for managing Minecraft servers via RCON
- **RCON**: Remote Console protocol used to send commands to Minecraft servers
- **Server**: A Minecraft server instance with IP address, RCON port, and credentials
- **User**: An authenticated person using the IronGate portal
- **Group**: A collection of Users with shared server access permissions
- **Whitelist**: A list of approved Minecraft usernames allowed to join a server
- **WhitelistRequest**: A record of a user's request to add a Minecraft username to a server's whitelist
- **RconHandler**: The service class responsible for establishing RCON connections and executing commands
- **Encryption Utility**: The cryptography service that encrypts/decrypts RCON passwords using Fernet

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to securely store RCON passwords, so that server credentials are protected from unauthorized access.

#### Acceptance Criteria

1. WHEN an administrator saves a Server with an RCON password THEN the IronGate SHALL encrypt the password using Fernet symmetric encryption from the cryptography library before storing it in the database
2. WHEN the IronGate retrieves an RCON password for use THEN the IronGate SHALL decrypt the stored encrypted password and return the plaintext value for RCON authentication
3. WHEN the encryption key is loaded THEN the IronGate SHALL read it from environment variables and never store it in the database or source code
4. WHEN a Server instance is created or updated THEN the IronGate SHALL ensure the RCON password is never stored in plaintext format or hashed format
5. WHEN the Encryption Utility is initialized THEN the IronGate SHALL use the cryptography library's Fernet class for symmetric encryption and decryption operations

### Requirement 2

**User Story:** As a system administrator, I want to assign users to groups and link groups to servers, so that I can control which users can access which servers.

#### Acceptance Criteria

1. WHEN an administrator creates a Server THEN the IronGate SHALL allow selection of one or more Groups that can access that Server
2. WHEN an administrator assigns a User to a Group THEN the IronGate SHALL grant that User access to all Servers linked to that Group
3. WHEN an administrator removes a User from a Group THEN the IronGate SHALL revoke that User's access to Servers exclusively linked to that Group
4. WHEN a User belongs to multiple Groups THEN the IronGate SHALL grant access to all Servers linked to any of those Groups

### Requirement 3

**User Story:** As an authenticated user, I want to view a dashboard of servers I can access, so that I can see which Minecraft servers are available to me.

#### Acceptance Criteria

1. WHEN a User accesses the dashboard THEN the IronGate SHALL display only Servers linked to Groups the User belongs to
2. WHEN a User belongs to no Groups THEN the IronGate SHALL display an empty server list with an informative message
3. WHEN a Server is linked to multiple Groups THEN the IronGate SHALL display that Server only once in the dashboard
4. WHEN an unauthenticated visitor accesses the dashboard THEN the IronGate SHALL redirect them to the login page

### Requirement 4

**User Story:** As an authenticated user, I want to view the list of online players on a server, so that I can see who is currently playing.

#### Acceptance Criteria

1. WHEN a User views a Server they have access to THEN the IronGate SHALL send the "list" command via RCON and display the online players
2. WHEN the RCON connection fails THEN the IronGate SHALL display an error message indicating the server is unreachable
3. WHEN the server response is parsed THEN the IronGate SHALL extract player usernames from the response text and display them as a structured list
4. WHEN the player list is displayed THEN the IronGate SHALL automatically refresh it every 30 seconds without full page reload
5. WHEN a User attempts to view players on a Server they do not have access to THEN the IronGate SHALL deny the request and return an authorization error

### Requirement 5

**User Story:** As an authenticated user, I want to request adding a Minecraft username to a server's whitelist, so that specific players can join the server.

#### Acceptance Criteria

1. WHEN a User submits a whitelist request with a valid Minecraft username THEN the IronGate SHALL create a WhitelistRequest record and send the "whitelist add" command via RCON
2. WHEN a User submits a whitelist request with an invalid username THEN the IronGate SHALL reject the request and display a validation error message
3. WHEN the RCON command succeeds THEN the IronGate SHALL update the WhitelistRequest status to PROCESSED and store the server response
4. WHEN the RCON command fails THEN the IronGate SHALL update the WhitelistRequest status to FAILED and store the error message
5. WHEN a User attempts to whitelist on a Server they do not have access to THEN the IronGate SHALL deny the request and return an authorization error

### Requirement 6

**User Story:** As a system administrator, I want to manage servers through the Django admin interface, so that I can configure server details and group assignments.

#### Acceptance Criteria

1. WHEN an administrator accesses the admin panel THEN the IronGate SHALL display interfaces for managing Servers, Users, Groups, and WhitelistRequests
2. WHEN an administrator creates a Server in the admin panel THEN the IronGate SHALL require name, IP address, RCON port, and RCON password fields
3. WHEN an administrator views a Server in the admin panel THEN the IronGate SHALL display the encrypted password field but not the plaintext password
4. WHEN an administrator edits Server group assignments THEN the IronGate SHALL provide a multi-select interface for linking Groups to the Server

### Requirement 7

**User Story:** As a developer, I want the RCON connection to handle errors gracefully, so that network issues or server downtime do not crash the application.

#### Acceptance Criteria

1. WHEN the RconHandler attempts to connect to a Server THEN the IronGate SHALL use a context manager to ensure connections are properly closed
2. WHEN an RCON connection times out THEN the RconHandler SHALL catch the timeout exception and return an error status
3. WHEN an RCON connection is refused THEN the RconHandler SHALL catch the connection exception and return an error status
4. WHEN an RCON command is executed THEN the RconHandler SHALL return both the success status and the server response message

### Requirement 8

**User Story:** As a security-conscious administrator, I want all Minecraft usernames validated before sending to RCON, so that command injection attacks are prevented.

#### Acceptance Criteria

1. WHEN a User submits a Minecraft username THEN the IronGate SHALL validate it against the regex pattern ^[a-zA-Z0-9_]{3,16}$ before any RCON command is executed
2. WHEN a username contains special characters other than underscore THEN the IronGate SHALL reject the input and display a validation error
3. WHEN a username is shorter than 3 characters or longer than 16 characters THEN the IronGate SHALL reject the input and display a validation error
4. WHEN a username passes validation THEN the IronGate SHALL allow it to be used in RCON commands
5. WHEN the WhitelistRequest logic processes a username THEN the IronGate SHALL perform validation before the username is ever sent to the RCON socket

### Requirement 9

**User Story:** As an authenticated user, I want to switch between English and Simplified Chinese, so that I can use the portal in my preferred language.

#### Acceptance Criteria

1. WHEN a User views any page in the IronGate portal THEN the IronGate SHALL support both English and Simplified Chinese languages using Django's i18n framework
2. WHEN a User clicks the language switcher in the navigation bar THEN the IronGate SHALL change all interface text, labels, and messages to the selected language
3. WHEN the IronGate renders templates THEN the IronGate SHALL use Django's trans template tag for all user-facing strings
4. WHEN the IronGate defines model fields and view messages THEN the IronGate SHALL use gettext_lazy for all translatable strings
5. WHEN the IronGate processes language selection THEN the IronGate SHALL use LocaleMiddleware to handle language switching and persistence

### Requirement 10

**User Story:** As an authenticated user, I want a responsive and modern interface, so that I can use the portal comfortably on different devices.

#### Acceptance Criteria

1. WHEN a User accesses the portal THEN the IronGate SHALL render pages using Bootstrap 5 for responsive layout
2. WHEN a User views the dashboard on a mobile device THEN the IronGate SHALL display server cards in a single column layout
3. WHEN a User views the dashboard on a desktop device THEN the IronGate SHALL display server cards in a multi-column grid layout
4. WHEN dynamic content updates occur THEN the IronGate SHALL use HTMX to update page sections without full page reload
