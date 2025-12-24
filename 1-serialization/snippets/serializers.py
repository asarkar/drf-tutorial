from rest_framework import serializers

from .models import Snippet


# ModelSerializer class provides a shortcut that automatically provides a full set of fields for
# the model, plus simple default implementations for the create() and update() methods.
class SnippetSerializer(serializers.ModelSerializer[Snippet]):
    class Meta:
        model = Snippet
        fields = ["id", "title", "code", "linenos", "language", "style"]
