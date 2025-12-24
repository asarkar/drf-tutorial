from django.urls import URLPattern, URLResolver, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SnippetDetail, SnippetList, UserDetail, UserList

urlpatterns: list[URLResolver | URLPattern] = [
    path("snippets/", SnippetList.as_view(), name="snippet-list"),
    path("snippets/<int:pk>/", SnippetDetail.as_view(), name="snippet-detail"),
    path("users/", UserList.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetail.as_view(), name="user-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
