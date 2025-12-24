import json
from typing import Any

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Snippet.objects.count(), 2)

    def test_list_method_not_allowed(self) -> None:
        """Test unsupported method on list endpoint."""
        response = self.client.delete(reverse("snippet-list"))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_snippet(self) -> None:
        """Test GET request to retrieve a single snippet."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "First Snippet")
        self.assertEqual(data["code"], "print('first')")

    def test_retrieve_snippet_not_found(self) -> None:
        """Test GET request for non-existent snippet."""
        response = self.client.get(reverse("snippet-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_snippet_not_found(self) -> None:
        """Test PUT request for non-existent snippet."""
        payload = {"title": "Test", "code": "test"}

        response = self.client.put(
            reverse("snippet-detail", kwargs={"pk": 9999}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_snippet(self) -> None:
        """Test DELETE request to remove a snippet."""
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Snippet.objects.count(), 1)
        self.assertFalse(Snippet.objects.filter(pk=self.snippet1.pk).exists())

    def test_delete_snippet_not_found(self) -> None:
        """Test DELETE request for non-existent snippet."""
        response = self.client.delete(reverse("snippet-detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_method_not_allowed(self) -> None:
        """Test unsupported method on detail endpoint."""
        response = self.client.post(reverse("snippet-detail", kwargs={"pk": self.snippet1.pk}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ContentNegotiationTests(TestCase):
    """Tests for content negotiation and format suffixes."""

    def setUp(self) -> None:
        """Set up test data."""
        self.snippet = Snippet.objects.create(
            title="Test Snippet",
            code="print('test')",
            language="python",
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
        response = self.client.post(
            reverse("snippet-list"),
            data={"code": "print(123)"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["code"], "print(123)")
        self.assertEqual(data["title"], "")
        self.assertEqual(data["language"], "python")

    def test_create_with_json_content_type(self) -> None:
        """Test POST request with JSON content type."""
        response = self.client.post(
            reverse("snippet-list"),
            data=json.dumps({"code": "print(456)"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data["code"], "print(456)")
        self.assertEqual(data["title"], "")
        self.assertEqual(data["language"], "python")
