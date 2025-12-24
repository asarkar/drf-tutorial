from django.contrib.auth.models import User
from rest_framework import generics, permissions
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
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView[User]):
    queryset = User.objects.all()
    serializer_class = UserSerializer
