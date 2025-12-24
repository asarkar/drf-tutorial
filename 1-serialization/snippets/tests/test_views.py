import json
from typing import Any

from django.test import TestCase
from django.urls import reverse

from snippets.models import Snippet


class SnippetViewTests(TestCase):
    """Tests for snippet views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.snippet1 = Snippet.objects.create(
            title="First Snippet",
            code="print('first')",
            language="python",
        )
        self.snippet2 = Snippet.objects.create(
            title="Second Snippet",
            code="console.log('second')",
            language="javascript",
        )

    def test_list_snippets(self) -> None:
        """Test GET request to list all snippets."""
        response = self.client.get(reverse("snippet-list"))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_create_snippet(self) -> None:
        """Test POST request to create a new snippet."""
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

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "New Snippet")
        self.assertEqual(data["code"], "print('new')")
        self.assertEqual(Snippet.objects.count(), 3)

    def test_create_snippet_invalid_data(self) -> None:
        """Test POST request with invalid data."""
        payload: dict[str, Any] = {"title": "No Code Field"}

        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_list_method_not_allowed(self) -> None:
        """Test unsupported method on list endpoint."""
        response = self.client.delete(reverse("snippet-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Method Not Allowed")

    def test_retrieve_snippet(self) -> None:
        """Test GET request to retrieve a single snippet."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "First Snippet")
        self.assertEqual(data["code"], "print('first')")

    def test_retrieve_snippet_not_found(self) -> None:
        """Test GET request for non-existent snippet."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, 404)

    def test_update_snippet(self) -> None:
        """Test PUT request to update a snippet."""
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

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Updated Title")

        self.snippet1.refresh_from_db()
        self.assertEqual(self.snippet1.title, "Updated Title")

    def test_update_snippet_invalid_data(self) -> None:
        """Test PUT request with invalid data."""
        payload: dict[str, Any] = {"title": "No Code"}

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_snippet_not_found(self) -> None:
        """Test PUT request for non-existent snippet."""
        payload = {"title": "Test", "code": "test"}

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": 9999}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_snippet(self) -> None:
        """Test DELETE request to remove a snippet."""
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertFalse(Snippet.objects.filter(pk=self.snippet1.pk).exists())

    def test_delete_snippet_not_found(self) -> None:
        """Test DELETE request for non-existent snippet."""
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, 404)

    def test_detail_method_not_allowed(self) -> None:
        """Test unsupported method on detail endpoint."""
        response = self.client.patch(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Method Not Allowed")
