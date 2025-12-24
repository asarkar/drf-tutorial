from django.urls import URLPattern, URLResolver, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SnippetDetail, SnippetHighlight, SnippetList, UserDetail, UserList, api_root

urlpatterns: list[URLResolver | URLPattern] = [
    path("", api_root, name="api-root"),
    path("snippets/", SnippetList.as_view(), name="snippet-list"),
    path("snippets/<int:pk>/", SnippetDetail.as_view(), name="snippet-detail"),
    path("users/", UserList.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetail.as_view(), name="user-detail"),
    path("snippets/<int:pk>/highlight/", SnippetHighlight.as_view(), name="snippet-highlight"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
