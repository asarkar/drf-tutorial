from django.urls import URLPattern, URLResolver, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import snippet_detail, snippet_list

urlpatterns: list[URLResolver | URLPattern] = [
    path("snippets/", snippet_list, name="snippet-list"),
    path("snippets/<int:pk>/", snippet_detail, name="snippet-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
