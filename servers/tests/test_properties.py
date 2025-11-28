"""
Property-Based Tests for IronGate
Tests universal properties using Hypothesis
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from servers.utils.encryption import get_encryption_utility


@pytest.mark.property
class TestEncryptionProperties:
    """Property-based tests for encryption functionality"""
    
    @given(password=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_password_encryption_roundtrip(self, password):
        """
        Feature: irongate-minecraft-rcon-portal, Property 1: Password encryption round-trip
        
        For any RCON password string, encrypting it and then decrypting the result 
        should produce the original password value.
        
        Validates: Requirements 1.1, 1.2
        """
        encryption_util = get_encryption_utility()
        
        # Encrypt the password
        encrypted = encryption_util.encrypt(password)
        
        # Decrypt it back
        decrypted = encryption_util.decrypt(encrypted)
        
        # Should get the original password back
        assert decrypted == password, \
            f"Round-trip failed: original='{password}', decrypted='{decrypted}'"
    
    @given(password=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_encrypted_data_is_not_plaintext(self, password):
        """
        Feature: irongate-minecraft-rcon-portal, Property 2: Encrypted passwords are never plaintext
        
        For any password, the encrypted data should be binary and not equal to the plaintext.
        
        Validates: Requirements 1.4
        """
        encryption_util = get_encryption_utility()
        
        # Encrypt the password
        encrypted = encryption_util.encrypt(password)
        
        # Encrypted data should be bytes
        assert isinstance(encrypted, bytes), \
            "Encrypted data must be bytes"
        
        # Encrypted data should not be equal to the plaintext
        password_bytes = password.encode('utf-8')
        assert encrypted != password_bytes, \
            f"Encrypted data is identical to plaintext!"
        
        # Encrypted data should be longer than plaintext (Fernet adds overhead)
        assert len(encrypted) > len(password_bytes), \
            "Encrypted data should be longer than plaintext due to Fernet overhead"


@pytest.mark.property
@pytest.mark.django_db
class TestServerModelProperties:
    """Property-based tests for Server model"""
    
    @given(password=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_server_password_never_stored_as_plaintext(self, password):
        """
        Feature: irongate-minecraft-rcon-portal, Property 2: Encrypted passwords are never plaintext
        
        For any Server instance with a password, the value stored in the 
        rcon_password_encrypted field should be binary encrypted data, not the plaintext password string.
        
        Validates: Requirements 1.4
        """
        from servers.models import Server
        
        # Create a server instance (not saved to DB)
        server = Server(
            name="Test Server",
            ip_address="127.0.0.1",
            rcon_port=25575
        )
        
        # Set the password
        server.set_password(password)
        
        # Verify encrypted field is bytes
        assert isinstance(server.rcon_password_encrypted, bytes), \
            "Encrypted password must be stored as bytes"
        
        # Verify encrypted data is not equal to plaintext
        password_bytes = password.encode('utf-8')
        assert server.rcon_password_encrypted != password_bytes, \
            "Password is stored in plaintext!"
        
        # Verify we can decrypt it back
        decrypted = server.get_password()
        assert decrypted == password, \
            f"Decryption failed: expected '{password}', got '{decrypted}'"



@pytest.mark.property
@pytest.mark.django_db
class TestUsernameValidationProperties:
    """Property-based tests for Minecraft username validation"""
    
    # Custom strategy for VALID Minecraft usernames
    @staticmethod
    def valid_minecraft_usernames():
        """Generate valid Minecraft usernames matching ^[a-zA-Z0-9_]{3,16}$"""
        import string
        valid_chars = string.ascii_letters + string.digits + '_'
        return st.text(
            alphabet=valid_chars,
            min_size=3,
            max_size=16
        )
    
    # Custom strategy for INVALID Minecraft usernames
    @staticmethod
    def invalid_minecraft_usernames():
        """Generate invalid Minecraft usernames (wrong length or invalid characters)"""
        import string
        valid_chars = string.ascii_letters + string.digits + '_'
        special_chars = ' !@#$%^&*()[]{}|;:,.<>?/\\-+=~`"\''
        
        return st.one_of(
            # Too short (0-2 characters)
            st.text(alphabet=valid_chars, min_size=0, max_size=2),
            # Too long (17+ characters)
            st.text(alphabet=valid_chars, min_size=17, max_size=50),
            # Contains special characters (use sampled_from as suggested)
            st.text(alphabet=special_chars, min_size=3, max_size=16),
            # Mix of valid and invalid characters
            st.text(alphabet=valid_chars + special_chars, min_size=3, max_size=16).filter(
                lambda s: any(c in special_chars for c in s)
            ),
        )
    
    @given(username=valid_minecraft_usernames())
    @settings(max_examples=100, deadline=500)
    def test_valid_usernames_are_accepted(self, username):
        """
        Feature: irongate-minecraft-rcon-portal, Property 12: Invalid username is rejected
        
        For any string that matches the regex pattern ^[a-zA-Z0-9_]{3,16}$,
        the validation should pass and allow the username.
        
        Validates: Requirements 5.2, 8.1, 8.2, 8.3, 8.4
        """
        from django.contrib.auth.models import User
        from servers.models import Server, WhitelistRequest
        
        # Create test user and server
        user = User.objects.create_user(username='testuser', password='testpass')
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        server.save()
        
        # Create whitelist request with valid username
        request = WhitelistRequest(
            user=user,
            server=server,
            minecraft_username=username
        )
        
        # Should not raise validation error
        try:
            request.full_clean()  # This runs all validators
            assert True, f"Valid username '{username}' was accepted"
        except Exception as e:
            pytest.fail(f"Valid username '{username}' was rejected: {e}")
        finally:
            # Cleanup
            server.delete()
            user.delete()
    
    @given(username=invalid_minecraft_usernames())
    @settings(max_examples=100, deadline=500, suppress_health_check=[HealthCheck.filter_too_much])
    def test_invalid_usernames_are_rejected(self, username):
        """
        Feature: irongate-minecraft-rcon-portal, Property 12: Invalid username is rejected
        
        For any string that does not match the regex pattern ^[a-zA-Z0-9_]{3,16}$,
        submitting it as a Minecraft username should be rejected with a validation error
        before any RCON command is executed.
        
        Validates: Requirements 5.2, 8.1, 8.2, 8.3, 8.4
        """
        from django.core.exceptions import ValidationError
        from django.contrib.auth.models import User
        from servers.models import Server, WhitelistRequest
        import re
        
        # Skip if username happens to be valid (edge case)
        if re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
            return
        
        # Create test user and server
        user = User.objects.create_user(username='testuser2', password='testpass')
        server = Server(name="Test2", ip_address="127.0.0.2", rcon_port=25575)
        server.set_password("test")
        server.save()
        
        # Create whitelist request with invalid username
        request = WhitelistRequest(
            user=user,
            server=server,
            minecraft_username=username
        )
        
        # Should raise validation error
        try:
            request.full_clean()  # This runs all validators
            # If we get here, validation didn't catch the invalid username
            pytest.fail(f"Invalid username '{username}' was incorrectly accepted!")
        except ValidationError as e:
            # Expected - invalid username was rejected
            assert 'minecraft_username' in e.message_dict, \
                f"ValidationError should be for minecraft_username field"
        finally:
            # Cleanup
            server.delete()
            user.delete()



@pytest.mark.property
class TestRconParserProperties:
    """Property-based tests for RCON response parsing"""
    
    @staticmethod
    def valid_minecraft_usernames_list():
        """Generate lists of valid Minecraft usernames"""
        import string
        valid_chars = string.ascii_letters + string.digits + '_'
        username_strategy = st.text(alphabet=valid_chars, min_size=3, max_size=16)
        return st.lists(username_strategy, min_size=0, max_size=20)
    
    @given(usernames=valid_minecraft_usernames_list())
    @settings(max_examples=100, deadline=500)
    def test_rcon_parser_extracts_all_players(self, usernames):
        """
        Feature: irongate-minecraft-rcon-portal, Property 9: RCON response parsing extracts players
        
        For any valid RCON "list" response string, the parser should correctly 
        extract all player usernames into a structured list.
        
        Validates: Requirements 4.3
        """
        from servers.services.rcon_manager import RconHandler
        
        # Construct a fake RCON response in the standard format
        player_count = len(usernames)
        max_players = 20
        
        if player_count == 0:
            # Empty server response
            fake_response = f"There are 0/{max_players} players online"
        else:
            # Server with players
            player_list = ", ".join(usernames)
            fake_response = f"There are {player_count}/{max_players} players online: {player_list}"
        
        # Create a mock server (we only need the parser method)
        # We'll test the parser directly without needing a real server
        from servers.models import Server
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        
        handler = RconHandler(server)
        
        # Parse the fake response
        parsed_players = handler._parse_player_list(fake_response)
        
        # Verify we got exactly the players we put in
        assert len(parsed_players) == len(usernames), \
            f"Expected {len(usernames)} players, got {len(parsed_players)}"
        
        assert parsed_players == usernames, \
            f"Player list mismatch: expected {usernames}, got {parsed_players}"
    
    @given(usernames=valid_minecraft_usernames_list())
    @settings(max_examples=100, deadline=500)
    def test_rcon_parser_handles_alternative_format(self, usernames):
        """
        Test parser handles alternative RCON response format.
        
        Some servers use "There are X of a max of Y players online:" format.
        """
        from servers.services.rcon_manager import RconHandler
        from servers.models import Server
        
        # Construct alternative format response
        player_count = len(usernames)
        max_players = 20
        
        if player_count == 0:
            fake_response = f"There are 0 of a max of {max_players} players online:"
        else:
            player_list = ", ".join(usernames)
            fake_response = f"There are {player_count} of a max of {max_players} players online: {player_list}"
        
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        handler = RconHandler(server)
        
        # Parse the fake response
        parsed_players = handler._parse_player_list(fake_response)
        
        # Verify correctness
        assert len(parsed_players) == len(usernames)
        assert parsed_players == usernames



@pytest.mark.property
class TestRconHandlerReturnStructure:
    """Property-based tests for RCON handler return value structure"""
    
    def test_get_players_returns_structured_response(self):
        """
        Feature: irongate-minecraft-rcon-portal, Property 16: RCON handler returns structured response
        
        For any RCON command executed by RconHandler, the return value should be 
        a dictionary containing both a success status boolean and a message string.
        
        Validates: Requirements 7.4
        """
        from servers.services.rcon_manager import RconHandler
        from servers.models import Server
        from unittest.mock import patch, MagicMock
        
        # Create a test server
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        
        handler = RconHandler(server)
        
        # Mock the RCON connection to simulate success
        with patch('servers.services.rcon_manager.MCRcon') as mock_rcon_class:
            mock_rcon = MagicMock()
            mock_rcon.command.return_value = "There are 2/20 players online: Steve, Alex"
            mock_rcon_class.return_value = mock_rcon
            
            result = handler.get_players()
            
            # Verify structure
            assert isinstance(result, dict), "Result must be a dictionary"
            assert 'success' in result, "Result must contain 'success' key"
            assert 'message' in result, "Result must contain 'message' key"
            assert 'players' in result, "get_players result must contain 'players' key"
            
            # Verify types
            assert isinstance(result['success'], bool), "'success' must be a boolean"
            assert isinstance(result['message'], str), "'message' must be a string"
            assert isinstance(result['players'], list), "'players' must be a list"
    
    def test_add_whitelist_returns_structured_response(self):
        """
        Test that add_whitelist returns structured response.
        
        Validates: Requirements 7.4
        """
        from servers.services.rcon_manager import RconHandler
        from servers.models import Server
        from unittest.mock import patch, MagicMock
        
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        
        handler = RconHandler(server)
        
        # Mock successful whitelist add
        with patch('servers.services.rcon_manager.MCRcon') as mock_rcon_class:
            mock_rcon = MagicMock()
            mock_rcon.command.return_value = "Added TestPlayer to whitelist"
            mock_rcon_class.return_value = mock_rcon
            
            result = handler.add_whitelist("TestPlayer")
            
            # Verify structure
            assert isinstance(result, dict), "Result must be a dictionary"
            assert 'success' in result, "Result must contain 'success' key"
            assert 'message' in result, "Result must contain 'message' key"
            
            # Verify types
            assert isinstance(result['success'], bool), "'success' must be a boolean"
            assert isinstance(result['message'], str), "'message' must be a string"
    
    def test_error_responses_have_correct_structure(self):
        """
        Test that error responses also follow the structured format.
        
        Validates: Requirements 7.4
        """
        from servers.services.rcon_manager import RconHandler
        from servers.models import Server
        from unittest.mock import patch
        import socket
        
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test")
        
        handler = RconHandler(server)
        
        # Mock connection timeout
        with patch('servers.services.rcon_manager.MCRcon') as mock_rcon_class:
            mock_rcon_class.side_effect = socket.timeout("Connection timed out")
            
            result = handler.get_players()
            
            # Verify error response structure
            assert isinstance(result, dict), "Error result must be a dictionary"
            assert 'success' in result, "Error result must contain 'success' key"
            assert 'message' in result, "Error result must contain 'message' key"
            assert result['success'] is False, "Error result 'success' must be False"
            assert isinstance(result['message'], str), "'message' must be a string"
            assert len(result['message']) > 0, "'message' must not be empty"



@pytest.mark.property
class TestVersionContextProcessorProperties:
    """Property-based tests for version context processor"""
    
    @given(version_string=st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_version_display_consistency(self, version_string):
        """
        Feature: version-and-group-management, Property 1: Version display consistency
        
        For any version string written to the VERSION file, reading it through 
        the context processor should return the same string (with whitespace stripped).
        
        Validates: Requirements 1.1, 1.2
        """
        from servers.context_processors import version_context
        from django.conf import settings
        from unittest.mock import Mock
        import tempfile
        import os
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a temporary VERSION file
            version_file_path = os.path.join(tmp_dir, "VERSION")
            # Write with newline=None to match how the context processor reads
            with open(version_file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(version_string)
            
            # Mock settings.BASE_DIR to point to tmp_dir
            original_base_dir = settings.BASE_DIR
            try:
                settings.BASE_DIR = tmp_dir
                
                # Create a mock request
                mock_request = Mock()
                
                # Call the context processor
                result = version_context(mock_request)
                
                # Read the file the same way to get expected value
                with open(version_file_path, 'r', encoding='utf-8', newline=None) as f:
                    expected_version = f.read().strip()
                
                # Verify the result
                assert 'app_version' in result, "Result must contain 'app_version' key"
                assert result['app_version'] == expected_version, \
                    f"Version mismatch: expected '{expected_version}', got '{result['app_version']}'"
            finally:
                # Restore original BASE_DIR
                settings.BASE_DIR = original_base_dir
    
    @given(error_type=st.sampled_from(['missing', 'permission', 'empty']))
    @settings(max_examples=100)
    def test_version_fallback_handling(self, error_type):
        """
        Feature: version-and-group-management, Property 2: Version fallback handling
        
        For any file error condition (missing file, permission denied, corrupted content), 
        the context processor should return a valid string without raising exceptions.
        
        Validates: Requirements 1.3
        """
        from servers.context_processors import version_context
        from django.conf import settings
        from unittest.mock import Mock
        import tempfile
        import os
        import platform
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Mock settings.BASE_DIR to point to tmp_dir
            original_base_dir = settings.BASE_DIR
            try:
                settings.BASE_DIR = tmp_dir
                
                # Simulate different error conditions
                if error_type == 'missing':
                    # Don't create the file
                    pass
                elif error_type == 'permission':
                    # Create file but make it unreadable (skip on Windows)
                    if platform.system() != 'Windows':
                        version_file_path = os.path.join(tmp_dir, "VERSION")
                        with open(version_file_path, 'w', encoding='utf-8') as f:
                            f.write("test")
                        os.chmod(version_file_path, 0o000)
                    else:
                        # On Windows, just test missing file instead
                        pass
                elif error_type == 'empty':
                    # Create empty file
                    version_file_path = os.path.join(tmp_dir, "VERSION")
                    with open(version_file_path, 'w', encoding='utf-8') as f:
                        f.write("")
                
                # Create a mock request
                mock_request = Mock()
                
                # Call the context processor - should not raise exception
                try:
                    result = version_context(mock_request)
                    
                    # Verify the result structure
                    assert isinstance(result, dict), "Result must be a dictionary"
                    assert 'app_version' in result, "Result must contain 'app_version' key"
                    assert isinstance(result['app_version'], str), "'app_version' must be a string"
                    
                    # For empty file, should return empty string (stripped)
                    # For missing/permission errors, should return 'Unknown'
                    if error_type == 'empty':
                        assert result['app_version'] == '', "Empty file should return empty string"
                    else:
                        assert result['app_version'] == 'Unknown', \
                            f"Error condition should return 'Unknown', got '{result['app_version']}'"
                except Exception as e:
                    pytest.fail(f"Context processor raised exception: {e}")
            finally:
                # Restore original BASE_DIR
                settings.BASE_DIR = original_base_dir


@pytest.mark.property
class TestGroupFilteringProperties:
    """Property-based tests for group filtering functionality"""
    
    @given(group_name=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_default_group_identification(self, group_name):
        """
        Feature: version-and-group-management, Property 3: Default group identification
        
        For any group name, the is_default_group function should return True 
        if and only if the name contains " | " (Django's default format).
        
        Validates: Requirements 2.4
        """
        from servers.admin import is_default_group
        
        # Check if group name contains " | "
        has_pipe_separator = " | " in group_name
        
        # Function should return True only if name contains " | "
        result = is_default_group(group_name)
        
        assert result == has_pipe_separator, \
            f"is_default_group('{group_name}') returned {result}, expected {has_pipe_separator}"
    
    @pytest.mark.django_db
    @given(
        custom_group_names=st.lists(
            st.text(
                alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),  # Exclude surrogates and control chars
                min_size=1,
                max_size=50
            ).filter(lambda s: " | " not in s and s.strip()),
            min_size=0,
            max_size=10,
            unique=True
        ),
        default_group_names=st.lists(
            st.text(
                alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
                min_size=1,
                max_size=20
            ).filter(lambda s: s.strip()).map(lambda s: f"{s} | {s}"),
            min_size=0,
            max_size=10,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_group_filtering_completeness(self, custom_group_names, default_group_names):
        """
        Feature: version-and-group-management, Property 4: Group filtering completeness
        
        For any queryset of groups containing both default and custom groups, 
        applying the admin filter should return only groups where is_default_group returns False.
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        from django.contrib.auth.models import Group
        from django.contrib import admin
        from servers.admin import GroupAdmin
        from unittest.mock import Mock
        
        # Create test groups
        created_groups = []
        
        # Create custom groups (without " | ")
        for name in custom_group_names:
            if name.strip():  # Skip empty names
                group, _ = Group.objects.get_or_create(name=name)
                created_groups.append(group)
        
        # Create default groups (with " | ")
        for name in default_group_names:
            if name.strip() and " | " in name:  # Ensure it has the separator
                group, _ = Group.objects.get_or_create(name=name)
                created_groups.append(group)
        
        try:
            # Create admin instance and get filtered queryset
            admin_instance = GroupAdmin(Group, admin.site)
            mock_request = Mock()
            filtered_qs = admin_instance.get_queryset(mock_request)
            
            # Get all filtered group names
            filtered_names = set(filtered_qs.values_list('name', flat=True))
            
            # Verify: all custom groups should be in filtered results
            for name in custom_group_names:
                if name.strip():
                    assert name in filtered_names, \
                        f"Custom group '{name}' should be in filtered results"
            
            # Verify: no default groups should be in filtered results
            for name in default_group_names:
                if name.strip() and " | " in name:
                    assert name not in filtered_names, \
                        f"Default group '{name}' should NOT be in filtered results"
            
            # Verify: filtered results contain only custom groups
            for name in filtered_names:
                assert " | " not in name, \
                    f"Filtered results should not contain default group '{name}'"
        
        finally:
            # Cleanup: delete all created groups
            for group in created_groups:
                group.delete()
    
    @pytest.mark.django_db
    @given(
        num_users=st.integers(min_value=0, max_value=5),
        num_servers=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50, deadline=None)
    def test_group_statistics_accuracy(self, num_users, num_servers):
        """
        Feature: version-and-group-management, Property 7: Group statistics accuracy
        
        For any group with associated users and servers, the displayed user count 
        and server count should equal the actual number of related objects.
        
        Validates: Requirements 3.5
        """
        from django.contrib.auth.models import User, Group
        from django.contrib import admin
        from servers.models import Server
        from servers.admin import GroupAdmin
        
        # Create a test group
        group = Group.objects.create(name=f"TestGroup_{id(self)}")
        
        # Create users and add to group
        created_users = []
        for i in range(num_users):
            user = User.objects.create_user(
                username=f"testuser_{id(self)}_{i}",
                password="testpass"
            )
            user.groups.add(group)
            created_users.append(user)
        
        # Create servers and link to group
        created_servers = []
        for i in range(num_servers):
            server = Server(
                name=f"TestServer_{id(self)}_{i}",
                ip_address=f"192.168.1.{i+1}",
                rcon_port=25575
            )
            server.set_password("testpass")
            server.save()
            server.groups.add(group)
            created_servers.append(server)
        
        try:
            # Create admin instance
            admin_instance = GroupAdmin(Group, admin.site)
            
            # Get counts from admin methods
            user_count = admin_instance.user_count(group)
            server_count = admin_instance.server_count(group)
            
            # Verify counts match actual numbers
            assert user_count == num_users, \
                f"User count mismatch: expected {num_users}, got {user_count}"
            assert server_count == num_servers, \
                f"Server count mismatch: expected {num_servers}, got {server_count}"
            
            # Also verify against direct queries
            actual_user_count = group.user_set.count()
            actual_server_count = group.servers.count()
            
            assert user_count == actual_user_count, \
                f"User count doesn't match direct query: {user_count} vs {actual_user_count}"
            assert server_count == actual_server_count, \
                f"Server count doesn't match direct query: {server_count} vs {actual_server_count}"
        
        finally:
            # Cleanup
            for user in created_users:
                user.delete()
            for server in created_servers:
                server.delete()
            group.delete()
    
    @pytest.mark.django_db(transaction=True)
    @given(group_name=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1,
        max_size=150
    ).filter(lambda s: s.strip()))
    @settings(max_examples=50)
    def test_group_name_validation(self, group_name):
        """
        Feature: version-and-group-management, Property 5: Group name validation
        
        For any attempt to create a group with an empty name or duplicate name, 
        the system should raise a validation error.
        
        Validates: Requirements 3.2
        """
        from django.contrib.auth.models import Group
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError, transaction
        
        # Test 1: Create a group with valid name (should succeed)
        group1 = Group.objects.create(name=group_name)
        
        try:
            # Test 2: Try to create duplicate group (should fail)
            with transaction.atomic():
                try:
                    group2 = Group.objects.create(name=group_name)
                    # If we get here, duplicate was allowed (bad!)
                    group2.delete()
                    pytest.fail(f"Duplicate group name '{group_name}' was allowed!")
                except IntegrityError:
                    # Expected - duplicate names are not allowed
                    pass
            
            # Test 3: Try to create group with empty name (should fail)
            try:
                empty_group = Group(name="")
                empty_group.full_clean()  # This should raise ValidationError
                # If we get here, empty name was allowed (bad!)
                pytest.fail("Empty group name was allowed!")
            except ValidationError as e:
                # Expected - empty names are not allowed
                assert 'name' in e.message_dict, "ValidationError should be for name field"
        
        finally:
            # Cleanup
            group1.delete()
    
    @pytest.mark.django_db
    @given(
        num_users=st.integers(min_value=0, max_value=5),
        num_servers=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50, deadline=None)
    def test_group_association_cascade(self, num_users, num_servers):
        """
        Feature: version-and-group-management, Property 6: Group association cascade
        
        For any group with associated users and servers, deleting that group should 
        remove all many-to-many relationships while preserving the user and server objects themselves.
        
        Validates: Requirements 3.3, 3.4
        """
        from django.contrib.auth.models import User, Group
        from servers.models import Server
        
        # Create a test group
        group = Group.objects.create(name=f"TestGroup_{id(self)}")
        
        # Create users and add to group
        created_users = []
        for i in range(num_users):
            user = User.objects.create_user(
                username=f"testuser_{id(self)}_{i}",
                password="testpass"
            )
            user.groups.add(group)
            created_users.append(user)
        
        # Create servers and link to group
        created_servers = []
        for i in range(num_servers):
            server = Server(
                name=f"TestServer_{id(self)}_{i}",
                ip_address=f"192.168.1.{i+1}",
                rcon_port=25575
            )
            server.set_password("testpass")
            server.save()
            server.groups.add(group)
            created_servers.append(server)
        
        try:
            # Verify associations exist before deletion
            assert group.user_set.count() == num_users
            assert group.servers.count() == num_servers
            
            # Delete the group
            group.delete()
            
            # Verify all users still exist
            for user in created_users:
                assert User.objects.filter(id=user.id).exists(), \
                    f"User {user.username} was deleted when group was deleted!"
                # Verify user no longer has the group
                user.refresh_from_db()
                assert not user.groups.filter(name=f"TestGroup_{id(self)}").exists(), \
                    f"User {user.username} still has deleted group!"
            
            # Verify all servers still exist
            for server in created_servers:
                assert Server.objects.filter(id=server.id).exists(), \
                    f"Server {server.name} was deleted when group was deleted!"
                # Verify server no longer has the group
                server.refresh_from_db()
                assert not server.groups.filter(name=f"TestGroup_{id(self)}").exists(), \
                    f"Server {server.name} still has deleted group!"
        
        finally:
            # Cleanup
            for user in created_users:
                if User.objects.filter(id=user.id).exists():
                    user.delete()
            for server in created_servers:
                if Server.objects.filter(id=server.id).exists():
                    server.delete()


@pytest.mark.property
@pytest.mark.django_db
class TestAccessControlProperties:
    """Property-based tests for access control logic"""
    
    def test_group_membership_grants_server_access(self):
        """
        Feature: irongate-minecraft-rcon-portal, Property 3: Group membership grants server access
        
        For any User, Group, and set of Servers, when the User is added to the Group 
        and the Servers are linked to that Group, the User should have access to all those Servers.
        
        Validates: Requirements 2.2
        """
        from django.contrib.auth.models import User, Group
        from servers.models import Server
        
        # Create test data
        user = User.objects.create_user(username='testuser', password='pass')
        group = Group.objects.create(name='TestGroup')
        
        # Create servers
        server1 = Server(name='Server1', ip_address='192.168.1.1', rcon_port=25575)
        server1.set_password('pass1')
        server1.save()
        
        server2 = Server(name='Server2', ip_address='192.168.1.2', rcon_port=25575)
        server2.set_password('pass2')
        server2.save()
        
        # Link servers to group
        server1.groups.add(group)
        server2.groups.add(group)
        
        # Add user to group
        user.groups.add(group)
        
        # User should have access to both servers
        accessible_servers = Server.objects.filter(groups__in=user.groups.all()).distinct()
        
        assert server1 in accessible_servers, "User should have access to server1"
        assert server2 in accessible_servers, "User should have access to server2"
        assert accessible_servers.count() == 2, "User should have access to exactly 2 servers"
        
        # Cleanup
        user.delete()
        group.delete()
        server1.delete()
        server2.delete()
    
    def test_multiple_group_membership_provides_union_of_access(self):
        """
        Feature: irongate-minecraft-rcon-portal, Property 5: Multiple group membership provides union of server access
        
        For any User belonging to multiple Groups, the set of accessible Servers 
        should equal the union of all Servers linked to any of those Groups.
        
        Validates: Requirements 2.4
        """
        from django.contrib.auth.models import User, Group
        from servers.models import Server
        
        # Create test data
        user = User.objects.create_user(username='multiuser', password='pass')
        group1 = Group.objects.create(name='Group1')
        group2 = Group.objects.create(name='Group2')
        
        # Create servers
        server1 = Server(name='Server1', ip_address='192.168.1.1', rcon_port=25575)
        server1.set_password('pass1')
        server1.save()
        server1.groups.add(group1)
        
        server2 = Server(name='Server2', ip_address='192.168.1.2', rcon_port=25575)
        server2.set_password('pass2')
        server2.save()
        server2.groups.add(group2)
        
        server3 = Server(name='Server3', ip_address='192.168.1.3', rcon_port=25575)
        server3.set_password('pass3')
        server3.save()
        server3.groups.add(group1, group2)  # In both groups
        
        # Add user to both groups
        user.groups.add(group1, group2)
        
        # User should have access to all three servers (union)
        accessible_servers = Server.objects.filter(groups__in=user.groups.all()).distinct()
        
        assert server1 in accessible_servers
        assert server2 in accessible_servers
        assert server3 in accessible_servers
        assert accessible_servers.count() == 3, "User should have access to all 3 servers"
        
        # Cleanup
        user.delete()
        group1.delete()
        group2.delete()
        server1.delete()
        server2.delete()
        server3.delete()
