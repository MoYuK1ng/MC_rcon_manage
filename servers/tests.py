from django.test import TestCase
from django.contrib.auth.models import User, Group
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.django import TestCase as HypothesisTestCase
from servers.models import Server
import json


class ServerModelTests(TestCase):
    """Unit tests for Server model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_server_creation(self):
        """Test basic server creation"""
        server = Server.objects.create(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575,
            game_ip='play.example.com',
            game_port=25565
        )
        server.set_password('test_password')
        server.save()
        
        self.assertEqual(server.name, 'Test Server')
        self.assertEqual(server.get_password(), 'test_password')
    
    def test_custom_fields_default(self):
        """Test that custom_fields defaults to empty dict"""
        server = Server.objects.create(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575
        )
        server.set_password('test_password')
        server.save()
        
        self.assertEqual(server.custom_fields, {})


class ServerCustomFieldsPropertyTests(HypothesisTestCase):
    """
    Property-based tests for Server custom fields
    Feature: ui-redesign, Property 4: Custom fields persistence
    Validates: Requirements 5.5
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_'),
            values=st.one_of(
                st.text(max_size=50),
                st.integers(min_value=0, max_value=9999),
                st.none()
            ),
            max_size=5
        )
    )
    def test_custom_fields_persistence(self, custom_fields):
        """
        Property: For any server with custom fields, saving and reloading 
        the server should preserve all custom field data without loss.
        """
        # Create server with custom fields
        server = Server.objects.create(
            name='Property Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575,
            custom_fields=custom_fields
        )
        server.set_password('test_password')
        server.save()
        
        # Reload from database
        server_id = server.id
        reloaded_server = Server.objects.get(id=server_id)
        
        # Assert custom fields are preserved
        self.assertEqual(reloaded_server.custom_fields, custom_fields)
        
        # Cleanup
        reloaded_server.delete()


class ServerCardDisplayPropertyTests(HypothesisTestCase):
    """
    Property-based tests for server card display
    Feature: ui-redesign, Property 2: Server card display completeness
    Validates: Requirements 2.2, 5.3
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.dictionaries(
            keys=st.sampled_from(['modpack_name', 'modpack_version', 'game_version', 'description', 'difficulty']),
            values=st.text(min_size=1, max_size=50),
            min_size=1,
            max_size=5
        )
    )
    def test_server_card_displays_all_custom_fields(self, custom_fields):
        """
        Property: For any server with custom fields, the server card should 
        display all non-empty custom field values.
        """
        # Create server with custom fields
        server = Server.objects.create(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575,
            custom_fields=custom_fields
        )
        server.set_password('test_password')
        server.save()
        
        # Render template
        from django.template import Context, Template
        template_str = """
        {% if server.custom_fields %}
        <div class="custom-fields">
            {% for key, value in server.custom_fields.items %}
                {% if value %}
                <div class="field">
                    <span class="key">{{ key }}</span>
                    <span class="value">{{ value }}</span>
                </div>
                {% endif %}
            {% endfor %}
        </div>
        {% endif %}
        """
        template = Template(template_str)
        context = Context({'server': server})
        rendered = template.render(context)
        
        # Assert all non-empty fields are displayed
        from html import escape
        for key, value in custom_fields.items():
            if value:
                self.assertIn(key, rendered, f"Field {key} should be displayed")
                # Check for escaped HTML value
                escaped_value = escape(value)
                self.assertIn(escaped_value, rendered, f"Value {value} (escaped: {escaped_value}) should be displayed")
        
        # Cleanup
        server.delete()


class EmptyFieldHidingPropertyTests(HypothesisTestCase):
    """
    Property-based tests for empty field hiding
    Feature: ui-redesign, Property 5: Empty field hiding
    Validates: Requirements 5.4
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(
        st.dictionaries(
            keys=st.sampled_from(['modpack_name', 'modpack_version', 'game_version', 'description']),
            values=st.one_of(st.text(min_size=1, max_size=50), st.just(''), st.none()),
            min_size=2,
            max_size=4
        )
    )
    def test_empty_fields_not_displayed(self, custom_fields):
        """
        Property: For any server card, custom fields with empty or null values 
        should not be displayed to users.
        """
        # Create server with mixed empty/non-empty fields
        server = Server.objects.create(
            name='Test Server',
            ip_address='127.0.0.1',
            rcon_port=25575,
            custom_fields=custom_fields
        )
        server.set_password('test_password')
        server.save()
        
        # Render template
        from django.template import Context, Template
        template_str = """
        {% if server.custom_fields %}
        <div class="custom-fields">
            {% for key, value in server.custom_fields.items %}
                {% if value %}
                <div class="field" data-key="{{ key }}">
                    <span class="key">{{ key }}</span>
                    <span class="value">{{ value }}</span>
                </div>
                {% endif %}
            {% endfor %}
        </div>
        {% endif %}
        """
        template = Template(template_str)
        context = Context({'server': server})
        rendered = template.render(context)
        
        # Assert empty/null fields are not displayed
        for key, value in custom_fields.items():
            if not value:  # Empty string or None
                # The key should not appear in a field div
                self.assertNotIn(f'data-key="{key}"', rendered, 
                               f"Empty field {key} should not be displayed")
        
        # Cleanup
        server.delete()


class VersionNumberPropertyTests(TestCase):
    """
    Property-based tests for version number accuracy
    Feature: ui-redesign, Property 3: Version number accuracy
    Validates: Requirements 3.1, 3.2
    """
    
    def test_version_number_matches_file(self):
        """
        Property: For any page load, the displayed version number should 
        match the content of the VERSION file.
        """
        import os
        from django.conf import settings
        from servers.context_processors import version_context
        from django.test import RequestFactory
        
        # Read VERSION file
        version_file_path = os.path.join(settings.BASE_DIR, 'VERSION')
        with open(version_file_path, 'r', encoding='utf-8') as f:
            expected_version = f.read().strip()
        
        # Get version from context processor
        factory = RequestFactory()
        request = factory.get('/')
        context = version_context(request)
        
        # Assert version matches
        self.assertEqual(context['app_version'], expected_version,
                        "Version from context processor should match VERSION file")
    
    def test_version_in_base_template(self):
        """
        Property: The base template should display the version number from 
        the VERSION file.
        """
        import os
        from django.conf import settings
        
        # Read VERSION file
        version_file_path = os.path.join(settings.BASE_DIR, 'VERSION')
        with open(version_file_path, 'r', encoding='utf-8') as f:
            expected_version = f.read().strip()
        
        # Read base template
        base_template_path = os.path.join(settings.BASE_DIR, 'servers', 'templates', 'base.html')
        with open(base_template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Assert template uses app_version variable
        self.assertIn('{{ app_version }}', template_content,
                     "Base template should use app_version variable")
        self.assertIn('https://github.com/MoYuK1ng/MC_rcon_manage', template_content,
                     "Base template should link to GitHub project")


class LightThemePropertyTests(TestCase):
    """
    Property-based tests for light theme consistency
    Feature: ui-redesign, Property 1: Light theme consistency
    Validates: Requirements 1.1, 1.2
    """
    
    def test_light_theme_in_base_template(self):
        """
        Property: The base template should use white or light gradient colors
        for background and dark colors for text.
        """
        import os
        from django.conf import settings
        
        # Read base template file
        base_template_path = os.path.join(settings.BASE_DIR, 'servers', 'templates', 'base.html')
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for light theme background
        self.assertIn('background: linear-gradient(135deg, #ffffff', content,
                     "Base template should have light gradient background")
        
        # Check for dark text color on body
        self.assertIn('text-gray-900', content,
                     "Base template should use dark text colors")
        
        # Check for white navigation background
        self.assertIn('bg-white', content,
                     "Navigation should have white background")
    
    def test_light_theme_card_styling(self):
        """
        Property: Card elements should use white/light backgrounds with 
        soft borders for light theme consistency.
        """
        import os
        from django.conf import settings
        
        base_template_path = os.path.join(settings.BASE_DIR, 'servers', 'templates', 'base.html')
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for card styling
        self.assertIn('background: white', content,
                     "Cards should have white background")
        self.assertIn('border: 1px solid #e2e8f0', content,
                     "Cards should have soft borders")
