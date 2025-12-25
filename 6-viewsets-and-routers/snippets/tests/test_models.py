from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Snippet


class SnippetModelTests(TestCase):
    """Tests for the Snippet model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_create_snippet_with_defaults(self) -> None:
        """Test creating a snippet with default values."""
        snippet = Snippet.objects.create(code="print('hello')", owner=self.user)

        self.assertEqual(snippet.code, "print('hello')")
        self.assertEqual(snippet.title, "")
        self.assertEqual(snippet.language, "python")
        self.assertEqual(snippet.style, "friendly")
        self.assertFalse(snippet.linenos)
        self.assertIsNotNone(snippet.created)
        self.assertEqual(snippet.owner, self.user)

    def test_create_snippet_with_custom_values(self) -> None:
        """Test creating a snippet with custom values."""
        snippet = Snippet.objects.create(
            title="My Snippet",
            code="console.log('hello')",
            linenos=True,
            language="javascript",
            style="monokai",
            owner=self.user,
        )

        self.assertEqual(snippet.title, "My Snippet")
        self.assertEqual(snippet.code, "console.log('hello')")
        self.assertTrue(snippet.linenos)
        self.assertEqual(snippet.language, "javascript")
        self.assertEqual(snippet.style, "monokai")

    def test_snippet_ordering(self) -> None:
        """Test that snippets are ordered by created date."""
        snippet1 = Snippet.objects.create(code="first", owner=self.user)
        snippet2 = Snippet.objects.create(code="second", owner=self.user)
        snippet3 = Snippet.objects.create(code="third", owner=self.user)

        snippets = list(Snippet.objects.all())

        self.assertEqual(snippets[0], snippet1)
        self.assertEqual(snippets[1], snippet2)
        self.assertEqual(snippets[2], snippet3)

    def test_snippet_highlighted_generated_on_save(self) -> None:
        """Test that highlighted HTML is generated when snippet is saved."""
        snippet = Snippet.objects.create(
            code="print('hello')",
            language="python",
            owner=self.user,
        )

        self.assertIsNotNone(snippet.highlighted)
        self.assertIn("print", snippet.highlighted)
        self.assertIn("<html>", snippet.highlighted.lower())

    def test_snippet_owner_relationship(self) -> None:
        """Test that snippet is accessible via user's snippets relation."""
        snippet = Snippet.objects.create(code="test", owner=self.user)

        self.assertIn(snippet, self.user.snippets.all())

    def test_snippet_deleted_with_owner(self) -> None:
        """Test that snippets are deleted when owner is deleted (CASCADE)."""
        Snippet.objects.create(code="test", owner=self.user)
        self.assertEqual(Snippet.objects.count(), 1)

        self.user.delete()

        self.assertEqual(Snippet.objects.count(), 0)
