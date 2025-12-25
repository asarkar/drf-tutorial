from django.test import TestCase

from ..models import Snippet


class SnippetModelTests(TestCase):
    """Tests for the Snippet model."""

    def test_create_snippet_with_defaults(self) -> None:
        """Test creating a snippet with default values."""
        snippet = Snippet.objects.create(code="print('hello')")

        self.assertEqual(snippet.code, "print('hello')")
        self.assertEqual(snippet.title, "")
        self.assertEqual(snippet.language, "python")
        self.assertEqual(snippet.style, "friendly")
        self.assertFalse(snippet.linenos)
        self.assertIsNotNone(snippet.created)

    def test_create_snippet_with_custom_values(self) -> None:
        """Test creating a snippet with custom values."""
        snippet = Snippet.objects.create(
            title="My Snippet",
            code="console.log('hello')",
            linenos=True,
            language="javascript",
            style="monokai",
        )

        self.assertEqual(snippet.title, "My Snippet")
        self.assertEqual(snippet.code, "console.log('hello')")
        self.assertTrue(snippet.linenos)
        self.assertEqual(snippet.language, "javascript")
        self.assertEqual(snippet.style, "monokai")

    def test_snippet_ordering(self) -> None:
        """Test that snippets are ordered by created date."""
        snippet1 = Snippet.objects.create(code="first")
        snippet2 = Snippet.objects.create(code="second")
        snippet3 = Snippet.objects.create(code="third")

        snippets = list(Snippet.objects.all())

        self.assertEqual(snippets[0], snippet1)
        self.assertEqual(snippets[1], snippet2)
        self.assertEqual(snippets[2], snippet3)
