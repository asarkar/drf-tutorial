from typing import Any

from django.test import TestCase

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


class SnippetSerializerTests(TestCase):
    """Tests for the SnippetSerializer."""

    def test_serialize_snippet(self) -> None:
        """Test serializing a snippet instance."""
        snippet = Snippet.objects.create(
            title="Test Snippet",
            code="print('test')",
            linenos=True,
            language="python",
            style="monokai",
        )

        serializer = SnippetSerializer(snippet)
        data = serializer.data

        self.assertEqual(data["id"], snippet.id)
        self.assertEqual(data["title"], "Test Snippet")
        self.assertEqual(data["code"], "print('test')")
        self.assertTrue(data["linenos"])
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["style"], "monokai")

    def test_serialize_multiple_snippets(self) -> None:
        """Test serializing multiple snippets."""
        Snippet.objects.create(code="first")
        Snippet.objects.create(code="second")

        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)

        self.assertEqual(len(serializer.data), 2)

    def test_deserialize_multiple_snippets(self) -> None:
        """Test deserializing multiple snippets with many=True."""
        data = [
            {"title": "First", "code": "print('first')", "language": "python"},
            {"title": "Second", "code": "console.log('second')", "language": "javascript"},
            {"title": "Third", "code": "puts 'third'", "language": "ruby"},
        ]

        serializer = SnippetSerializer(data=data, many=True)

        self.assertTrue(serializer.is_valid())
        snippets: list[Snippet] = serializer.save()  # type: ignore[assignment]
        self.assertEqual(len(snippets), 3)
        self.assertEqual(snippets[0].title, "First")
        self.assertEqual(snippets[1].title, "Second")
        self.assertEqual(snippets[2].title, "Third")
        self.assertEqual(Snippet.objects.count(), 3)

    def test_deserialize_valid_data(self) -> None:
        """Test deserializing valid data."""
        data = {
            "title": "New Snippet",
            "code": "print('new')",
            "linenos": False,
            "language": "python",
            "style": "friendly",
        }

        serializer = SnippetSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save()
        self.assertEqual(snippet.title, "New Snippet")
        self.assertEqual(snippet.code, "print('new')")

    def test_deserialize_minimal_data(self) -> None:
        """Test deserializing with only required fields."""
        data: dict[str, Any] = {"code": "minimal code"}

        serializer = SnippetSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save()
        self.assertEqual(snippet.code, "minimal code")
        self.assertEqual(snippet.title, "")  # default

    def test_deserialize_invalid_data_missing_code(self) -> None:
        """Test deserializing with missing required field."""
        data: dict[str, Any] = {"title": "No Code"}

        serializer = SnippetSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_update_snippet(self) -> None:
        """Test updating an existing snippet."""
        snippet = Snippet.objects.create(code="original")
        data = {"code": "updated", "title": "Updated Title"}

        serializer = SnippetSerializer(snippet, data=data)

        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.code, "updated")
        self.assertEqual(updated.title, "Updated Title")
