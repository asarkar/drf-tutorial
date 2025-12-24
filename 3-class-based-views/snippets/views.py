from rest_framework import generics

from .models import Snippet
from .serializers import SnippetSerializer


class SnippetList(generics.ListCreateAPIView[Snippet]):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView[Snippet]):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
