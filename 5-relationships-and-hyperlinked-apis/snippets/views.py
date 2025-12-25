from typing import Any

from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import BaseSerializer

from .models import Snippet
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer, UserSerializer


class SnippetList(generics.ListCreateAPIView[Snippet]):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: BaseSerializer[Snippet]) -> None:
        # The create() method of our serializer will now be passed an additional 'owner' field,
        # along with the validated data from the request.
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView[Snippet]):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class UserList(generics.ListAPIView[User]):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView[User]):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer


@api_view(["GET"])
def api_root(request: Request, format: str | None = None) -> Response:
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "snippets": reverse("snippet-list", request=request, format=format),
        }
    )


class SnippetHighlight(generics.GenericAPIView[Snippet]):
    queryset = Snippet.objects.all()
    # There are two styles of HTML renderer provided by DRF, one for dealing with
    # HTML rendered using templates, the other for dealing with pre-rendered HTML.
    # We're using the second one here.
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        snippet = self.get_object()
        return Response(snippet.highlighted)
