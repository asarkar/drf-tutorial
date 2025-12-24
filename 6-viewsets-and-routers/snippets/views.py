from typing import Any

from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import BaseSerializer

from .models import Snippet
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer, UserSerializer

# ViewSet classes are almost the same thing as View classes, except that they provide operations
# such as retrieve, or update, and not method handlers such as get or put.

# A ViewSet class is only bound to a set of method handlers at the last moment, when it is
# instantiated into a set of views, typically by using a Router class which handles the
# complexities of defining the URL conf for you.

# Notice that we've also used the @action decorator to create a custom action, named highlight.
# This decorator can be used to add any custom endpoints that don't fit into the standard
# create/update/delete style.

# Custom actions which use the @action decorator will respond to GET requests by default.
# We can use the methods argument if we wanted an action that responded to POST requests.

# The URLs for custom actions by default depend on the method name itself. If you want to change
# the way url should be constructed, you can include url_path as a decorator keyword argument.


class SnippetViewSet(viewsets.ModelViewSet[Snippet]):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """

    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer: BaseSerializer[Snippet]) -> None:
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

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
