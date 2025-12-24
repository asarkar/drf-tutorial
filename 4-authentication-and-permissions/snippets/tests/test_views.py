import json
from typing import Any

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from snippets.models import Snippet


class SnippetViewTests(TestCase):
    """Tests for snippet views with authentication."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        self.snippet1 = Snippet.objects.create(
            title="First Snippet",
            code="print('first')",
            language="python",
            owner=self.user1,
        )
        self.snippet2 = Snippet.objects.create(
            title="Second Snippet",
            code="console.log('second')",
            language="javascript",
            owner=self.user2,
        )

    def test_list_snippets_unauthenticated(self) -> None:
        """Test unauthenticated users can list snippets."""
        response = self.client.get(reverse("snippet-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_list_snippets_authenticated(self) -> None:
        """Test authenticated users can list snippets."""
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("snippet-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_create_snippet_unauthenticated(self) -> None:
        """Test unauthenticated users cannot create snippets."""
        payload = {"code": "print('new')"}

        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_create_snippet_authenticated(self) -> None:
        """Test authenticated users can create snippets."""
        self.client.login(username="user1", password="pass1")
        payload = {
            "title": "New Snippet",
            "code": "print('new')",
            "linenos": True,
            "language": "python",
            "style": "monokai",
        }

        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "New Snippet")
        self.assertEqual(data["owner"], "user1")
        self.assertEqual(Snippet.objects.count(), 3)

    def test_create_snippet_sets_owner(self) -> None:
        """Test that created snippet owner is set to the authenticated user."""
        self.client.login(username="user2", password="pass2")
        payload = {"code": "print('owned')"}

        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["owner"], "user2")

        snippet = Snippet.objects.get(pk=data["id"])
        self.assertEqual(snippet.owner, self.user2)

    def test_create_snippet_invalid_data(self) -> None:
        """Test POST request with invalid data."""
        self.client.login(username="user1", password="pass1")
        payload: dict[str, Any] = {"title": "No Code Field"}

        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_retrieve_snippet_unauthenticated(self) -> None:
        """Test unauthenticated users can retrieve snippets."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "First Snippet")
        self.assertEqual(data["owner"], "user1")

    def test_retrieve_snippet_not_found(self) -> None:
        """Test GET request for non-existent snippet."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_snippet_unauthenticated(self) -> None:
        """Test unauthenticated users cannot update snippets."""
        payload = {"code": "print('hacked')"}

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_snippet_as_owner(self) -> None:
        """Test owner can update their own snippet."""
        self.client.login(username="user1", password="pass1")
        payload = {
            "title": "Updated Title",
            "code": "print('updated')",
            "linenos": True,
            "language": "python",
            "style": "monokai",
        }

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Updated Title")

        self.snippet1.refresh_from_db()
        self.assertEqual(self.snippet1.title, "Updated Title")

    def test_update_snippet_as_non_owner(self) -> None:
        """Test non-owner cannot update another user's snippet."""
        self.client.login(username="user2", password="pass2")
        payload = {"code": "print('hacked')"}

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_snippet_unauthenticated(self) -> None:
        """Test unauthenticated users cannot delete snippets."""
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_delete_snippet_as_owner(self) -> None:
        """Test owner can delete their own snippet."""
        self.client.login(username="user1", password="pass1")
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertFalse(Snippet.objects.filter(pk=self.snippet1.pk).exists())

    def test_delete_snippet_as_non_owner(self) -> None:
        """Test non-owner cannot delete another user's snippet."""
        self.client.login(username="user2", password="pass2")
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_list_method_not_allowed(self) -> None:
        """Test unsupported method on list endpoint."""
        self.client.login(username="user1", password="pass1")
        response = self.client.delete(reverse("snippet-list"))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_method_not_allowed(self) -> None:
        """Test unsupported method on detail endpoint."""
        self.client.login(username="user1", password="pass1")
        response = self.client.post(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserViewTests(TestCase):
    """Tests for user views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user1 = User.objects.create_user(username="alice", password="pass1")
        self.user2 = User.objects.create_user(username="bob", password="pass2")

        self.snippet = Snippet.objects.create(
            code="print('test')",
            owner=self.user1,
        )

    def test_list_users(self) -> None:
        """Test listing all users."""
        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        usernames = [u["username"] for u in data]
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)

    def test_retrieve_user(self) -> None:
        """Test retrieving a single user."""
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["username"], "alice")
        self.assertIn("snippets", data)

    def test_retrieve_user_with_snippets(self) -> None:
        """Test that user detail includes their snippet IDs."""
        response = self.client.get(reverse("user-detail", kwargs={"pk": self.user1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["snippets"], [self.snippet.pk])

    def test_retrieve_user_not_found(self) -> None:
        """Test GET request for non-existent user."""
        response = self.client.get(reverse("user-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_list_method_not_allowed(self) -> None:
        """Test POST is not allowed on user list (read-only)."""
        response = self.client.post(
            reverse("user-list"),
            data=json.dumps({"username": "hacker"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_detail_method_not_allowed(self) -> None:
        """Test PUT/DELETE not allowed on user detail (read-only)."""
        response = self.client.put(
            reverse("user-detail", kwargs={"pk": self.user1.pk}),
            data=json.dumps({"username": "hacked"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ContentNegotiationTests(TestCase):
    """Tests for content negotiation and format suffixes."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.snippet = Snippet.objects.create(
            title="Test Snippet",
            code="print('test')",
            language="python",
            owner=self.user,
        )

    # Accept header tests

    def test_list_with_accept_json_header(self) -> None:
        """Test GET request with Accept: application/json header."""
        response = self.client.get(
            reverse("snippet-list"),
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertIsInstance(data, list)

    def test_list_with_accept_html_header(self) -> None:
        """Test GET request with Accept: text/html header returns browsable API."""
        response = self.client.get(
            reverse("snippet-list"),
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response["Content-Type"])

    def test_detail_with_accept_json_header(self) -> None:
        """Test GET detail with Accept: application/json header."""
        response = self.client.get(
            reverse("snippet-detail", kwargs={"pk": self.snippet.pk}),
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Test Snippet")

    # Format suffix tests

    def test_list_with_json_suffix(self) -> None:
        """Test GET request with .json format suffix."""
        response = self.client.get("/snippets.json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertIsInstance(data, list)

    def test_list_with_api_suffix(self) -> None:
        """Test GET request with .api format suffix returns browsable API."""
        response = self.client.get("/snippets.api")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response["Content-Type"])

    def test_detail_with_json_suffix(self) -> None:
        """Test GET detail with .json format suffix."""
        response = self.client.get(f"/snippets/{self.snippet.pk}.json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Test Snippet")

    def test_detail_with_api_suffix(self) -> None:
        """Test GET detail with .api format suffix returns browsable API."""
        response = self.client.get(f"/snippets/{self.snippet.pk}.api")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response["Content-Type"])

    # Content-Type header tests (request format)

    def test_create_with_form_data(self) -> None:
        """Test POST request with form data (application/x-www-form-urlencoded)."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("snippet-list"),
            data={"code": "print(123)"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["code"], "print(123)")
        self.assertEqual(data["owner"], "testuser")

    def test_create_with_json_content_type(self) -> None:
        """Test POST request with JSON content type."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps({"code": "print(456)"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["code"], "print(456)")
        self.assertEqual(data["owner"], "testuser")
