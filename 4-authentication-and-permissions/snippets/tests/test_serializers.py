from typing import Any

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Snippet
from ..serializers import SnippetSerializer, UserSerializer


class SnippetSerializerTests(TestCase):
    """Tests for the SnippetSerializer."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_serialize_snippet(self) -> None:
        """Test serializing a snippet instance."""
        snippet = Snippet.objects.create(
            title="Test Snippet",
            code="print('test')",
            linenos=True,
            language="python",
            style="monokai",
            owner=self.user,
        )

        serializer = SnippetSerializer(snippet)
        data = serializer.data

        self.assertEqual(data["id"], snippet.id)
        self.assertEqual(data["title"], "Test Snippet")
        self.assertEqual(data["code"], "print('test')")
        self.assertTrue(data["linenos"])
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["style"], "monokai")
        self.assertEqual(data["owner"], "testuser")

    def test_serialize_multiple_snippets(self) -> None:
        """Test serializing multiple snippets."""
        Snippet.objects.create(code="first", owner=self.user)
        Snippet.objects.create(code="second", owner=self.user)

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
        snippets: list[Snippet] = serializer.save(owner=self.user)  # type: ignore[assignment]
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
        snippet = serializer.save(owner=self.user)
        self.assertEqual(snippet.title, "New Snippet")
        self.assertEqual(snippet.code, "print('new')")
        self.assertEqual(snippet.owner, self.user)

    def test_deserialize_minimal_data(self) -> None:
        """Test deserializing with only required fields."""
        data: dict[str, Any] = {"code": "minimal code"}

        serializer = SnippetSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save(owner=self.user)
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
        snippet = Snippet.objects.create(code="original", owner=self.user)
        data = {"code": "updated", "title": "Updated Title"}

        serializer = SnippetSerializer(snippet, data=data)

        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.code, "updated")
        self.assertEqual(updated.title, "Updated Title")

    def test_owner_is_read_only(self) -> None:
        """Test that owner field is read-only and cannot be set via data."""
        other_user = User.objects.create_user(username="other", password="pass")
        data = {
            "code": "print('test')",
            "owner": other_user.username,  # Try to set owner via data
        }

        serializer = SnippetSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save(owner=self.user)
        # Owner should be self.user, not other_user
        self.assertEqual(snippet.owner, self.user)


class UserSerializerTests(TestCase):
    """Tests for the UserSerializer."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="alice", password="pass")

    def test_serialize_user(self) -> None:
        """Test serializing a user instance."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], "alice")
        self.assertIn("snippets", data)
        self.assertEqual(data["snippets"], [])

    def test_serialize_user_with_snippets(self) -> None:
        """Test serializing a user with snippets shows snippet IDs."""
        snippet1 = Snippet.objects.create(code="first", owner=self.user)
        snippet2 = Snippet.objects.create(code="second", owner=self.user)

        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["username"], "alice")
        self.assertEqual(set(data["snippets"]), {snippet1.pk, snippet2.pk})

    def test_serialize_multiple_users(self) -> None:
        """Test serializing multiple users."""
        User.objects.create_user(username="bob", password="pass")

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        self.assertEqual(len(serializer.data), 2)
        usernames = [u["username"] for u in serializer.data]
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)
