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
