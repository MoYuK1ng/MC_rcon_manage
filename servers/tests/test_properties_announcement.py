"""
Property-based tests for Announcement model
Tests correctness properties using Hypothesis
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.utils import timezone
from servers.models import Announcement


# Custom strategies for generating test data
chinese_text = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lo',),
        min_codepoint=0x4E00,
        max_codepoint=0x9FFF
    ),
    min_size=1,
    max_size=200
)

html_content = st.one_of(
    st.just('<p>Test paragraph</p>'),
    st.just('<strong>Bold text</strong>'),
    st.just('Line 1<br>Line 2'),
    st.just('<a href="#">Link</a>'),
    st.just('<em>Italic</em> and <strong>bold</strong>'),
)


class TestAnnouncementProperties(TestCase):
    """Property-based tests for Announcement model"""
    
    def tearDown(self):
        """Clean up after each test"""
        Announcement.objects.all().delete()
    
    @given(
        title=st.text(min_size=1, max_size=200),
        content=st.text(min_size=1, max_size=1000),
        is_active=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_content_integrity(self, title, content, is_active):
        """
        **Feature: admin-display-settings, Property 6: Announcement content integrity**
        
        For any announcement created with a title, content, and timestamp,
        retrieving that announcement from the database should return all fields intact.
        
        Validates: Requirements 3.1, 4.2
        """
        # Create announcement
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            is_active=is_active
        )
        
        # Retrieve announcement
        retrieved = Announcement.objects.get(pk=announcement.pk)
        
        # Verify all fields are intact
        assert retrieved.title == title
        assert retrieved.content == content
        assert retrieved.is_active == is_active
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
    
    @given(
        announcements=st.lists(
            st.booleans(),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_visibility_by_active_status(self, announcements):
        """
        **Feature: admin-display-settings, Property 4: Announcement visibility by active status**
        
        For any set of announcements, only those with is_active=True should be
        included when filtering by is_active=True.
        
        Validates: Requirements 3.2, 3.3
        """
        # Create announcements with different active statuses
        created = []
        for i, is_active in enumerate(announcements):
            ann = Announcement.objects.create(
                title=f"Announcement {i}",
                content=f"Content {i}",
                is_active=is_active
            )
            created.append(ann)
        
        # Query active announcements
        active_announcements = Announcement.objects.filter(is_active=True)
        
        # Count expected active announcements
        expected_active_count = sum(1 for a in announcements if a)
        
        # Verify count matches
        assert active_announcements.count() == expected_active_count
        
        # Verify all returned announcements are active
        for ann in active_announcements:
            assert ann.is_active == True
    
    @given(
        count=st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=50)
    def test_property_announcement_ordering(self, count):
        """
        **Feature: admin-display-settings, Property 5: Announcement ordering**
        
        For any set of active announcements, they should be ordered in reverse
        chronological order with the most recently created announcement appearing first.
        
        Validates: Requirements 3.4
        """
        # Create multiple announcements
        created_announcements = []
        for i in range(count):
            ann = Announcement.objects.create(
                title=f"Announcement {i}",
                content=f"Content {i}",
                is_active=True
            )
            created_announcements.append(ann)
        
        # Retrieve all announcements
        retrieved = list(Announcement.objects.all())
        
        # Verify they are in reverse chronological order
        for i in range(len(retrieved) - 1):
            assert retrieved[i].created_at >= retrieved[i + 1].created_at
    
    @given(
        content=html_content
    )
    @settings(max_examples=100)
    def test_property_html_preservation(self, content):
        """
        **Feature: admin-display-settings, Property 7: HTML content preservation**
        
        For any announcement content containing HTML tags, the content should be
        stored without modification.
        
        Validates: Requirements 3.5
        """
        # Create announcement with HTML content
        announcement = Announcement.objects.create(
            title="HTML Test",
            content=content,
            is_active=True
        )
        
        # Retrieve announcement
        retrieved = Announcement.objects.get(pk=announcement.pk)
        
        # Verify HTML is preserved exactly
        assert retrieved.content == content
        
        # Verify HTML tags are present (not escaped)
        if '<' in content and '>' in content:
            assert '<' in retrieved.content
            assert '>' in retrieved.content
    
    @given(
        title=chinese_text,
        content=chinese_text
    )
    @settings(max_examples=100)
    def test_property_unicode_support(self, title, content):
        """
        **Feature: admin-display-settings, Property 8: Unicode content support**
        
        For any announcement containing Chinese characters or other Unicode content,
        the content should be stored and retrieved without corruption.
        
        Validates: Requirements 4.5
        """
        # Create announcement with Chinese content
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            is_active=True
        )
        
        # Retrieve announcement
        retrieved = Announcement.objects.get(pk=announcement.pk)
        
        # Verify Chinese characters are preserved
        assert retrieved.title == title
        assert retrieved.content == content
        
        # Verify the content is still valid Unicode
        assert isinstance(retrieved.title, str)
        assert isinstance(retrieved.content, str)
