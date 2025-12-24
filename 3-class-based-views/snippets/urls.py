from django.urls import URLPattern, URLResolver, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SnippetDetail, SnippetList

urlpatterns: list[URLResolver | URLPattern] = [
    path("snippets/", SnippetList.as_view(), name="snippet-list"),
    path("snippets/<int:pk>/", SnippetDetail.as_view(), name="snippet-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
