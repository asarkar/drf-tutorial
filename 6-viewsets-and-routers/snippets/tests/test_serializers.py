from typing import Any

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ..models import Snippet
from ..serializers import SnippetSerializer, UserSerializer


class SnippetSerializerTests(TestCase):
    """Tests for the SnippetSerializer (HyperlinkedModelSerializer)."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def _get_serializer_context(self) -> dict[str, Any]:
        """Get context with request for hyperlinked serializers."""
        return {"request": self.request}

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

        serializer = SnippetSerializer(snippet, context=self._get_serializer_context())
        data = serializer.data

        self.assertEqual(data["id"], snippet.id)
        self.assertEqual(data["title"], "Test Snippet")
        self.assertEqual(data["code"], "print('test')")
        self.assertTrue(data["linenos"])
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["style"], "monokai")
        self.assertEqual(data["owner"], "testuser")
        # HyperlinkedModelSerializer adds url and highlight fields
        self.assertIn("url", data)
        self.assertIn("highlight", data)

    def test_serialize_snippet_url_format(self) -> None:
        """Test that serialized snippet contains proper URLs."""
        snippet = Snippet.objects.create(
            code="print('test')",
            owner=self.user,
        )

        serializer = SnippetSerializer(snippet, context=self._get_serializer_context())
        data = serializer.data

        self.assertIn(f"/snippets/{snippet.pk}/", data["url"])
        self.assertIn(f"/snippets/{snippet.pk}/highlight/", data["highlight"])

    def test_serialize_multiple_snippets(self) -> None:
        """Test serializing multiple snippets."""
        Snippet.objects.create(code="first", owner=self.user)
        Snippet.objects.create(code="second", owner=self.user)

        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True, context=self._get_serializer_context())

        self.assertEqual(len(serializer.data), 2)
        for snippet_data in serializer.data:
            self.assertIn("url", snippet_data)
            self.assertIn("highlight", snippet_data)

    def test_deserialize_valid_data(self) -> None:
        """Test deserializing valid data."""
        data = {
            "title": "New Snippet",
            "code": "print('new')",
            "linenos": False,
            "language": "python",
            "style": "friendly",
        }

        serializer = SnippetSerializer(data=data, context=self._get_serializer_context())

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save(owner=self.user)
        self.assertEqual(snippet.title, "New Snippet")
        self.assertEqual(snippet.code, "print('new')")
        self.assertEqual(snippet.owner, self.user)

    def test_deserialize_minimal_data(self) -> None:
        """Test deserializing with only required fields."""
        data: dict[str, Any] = {"code": "minimal code"}

        serializer = SnippetSerializer(data=data, context=self._get_serializer_context())

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save(owner=self.user)
        self.assertEqual(snippet.code, "minimal code")
        self.assertEqual(snippet.title, "")  # default

    def test_deserialize_invalid_data_missing_code(self) -> None:
        """Test deserializing with missing required field."""
        data: dict[str, Any] = {"title": "No Code"}

        serializer = SnippetSerializer(data=data, context=self._get_serializer_context())

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_update_snippet(self) -> None:
        """Test updating an existing snippet."""
        snippet = Snippet.objects.create(code="original", owner=self.user)
        data = {"code": "updated", "title": "Updated Title"}

        serializer = SnippetSerializer(snippet, data=data, context=self._get_serializer_context())

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

        serializer = SnippetSerializer(data=data, context=self._get_serializer_context())

        self.assertTrue(serializer.is_valid())
        snippet = serializer.save(owner=self.user)
        # Owner should be self.user, not other_user
        self.assertEqual(snippet.owner, self.user)


class UserSerializerTests(TestCase):
    """Tests for the UserSerializer with hyperlinked snippets."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="alice", password="pass")
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def _get_serializer_context(self) -> dict[str, Any]:
        """Get context with request for hyperlinked serializers."""
        return {"request": self.request}

    def test_serialize_user(self) -> None:
        """Test serializing a user instance."""
        serializer = UserSerializer(self.user, context=self._get_serializer_context())
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], "alice")
        self.assertIn("snippets", data)
        self.assertEqual(data["snippets"], [])
        self.assertIn("url", data)

    def test_serialize_user_url_format(self) -> None:
        """Test that serialized user contains proper URL."""
        serializer = UserSerializer(self.user, context=self._get_serializer_context())
        data = serializer.data

        self.assertIn(f"/users/{self.user.pk}/", data["url"])

    def test_serialize_user_with_hyperlinked_snippets(self) -> None:
        """Test serializing a user with snippets shows hyperlinks."""
        snippet1 = Snippet.objects.create(code="first", owner=self.user)
        snippet2 = Snippet.objects.create(code="second", owner=self.user)

        serializer = UserSerializer(self.user, context=self._get_serializer_context())
        data = serializer.data

        self.assertEqual(data["username"], "alice")
        self.assertEqual(len(data["snippets"]), 2)
        # Snippets should be URLs, not IDs
        snippet_urls = data["snippets"]
        self.assertTrue(any(f"/snippets/{snippet1.pk}/" in url for url in snippet_urls))
        self.assertTrue(any(f"/snippets/{snippet2.pk}/" in url for url in snippet_urls))

    def test_serialize_multiple_users(self) -> None:
        """Test serializing multiple users."""
        User.objects.create_user(username="bob", password="pass")

        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context=self._get_serializer_context())

        self.assertEqual(len(serializer.data), 2)
        usernames = [u["username"] for u in serializer.data]
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)
        for user_data in serializer.data:
            self.assertIn("url", user_data)
