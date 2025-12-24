from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Snippet


class SnippetSerializer(serializers.ModelSerializer[Snippet]):
    # We could have also used CharField(read_only=True) instead of ReadOnlyField
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Snippet
        fields = ["id", "title", "code", "linenos", "language", "style", "owner"]


class UserSerializer(serializers.ModelSerializer[User]):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        # Because 'snippets' is a reverse relationship on the User model, it will not be included
        # by default when using the ModelSerializer class, so we needed to add an explicit field
        # for it.
        fields = ["id", "username", "snippets"]
