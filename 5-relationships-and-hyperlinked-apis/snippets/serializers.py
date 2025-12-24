from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Snippet

# The HyperlinkedModelSerializer has the following differences from ModelSerializer:
# * It does not include the id field by default.
# * It includes a url field, using HyperlinkedIdentityField.
# * Relationships use HyperlinkedRelatedField, instead of PrimaryKeyRelatedField.
#
# Notice that we've also added a new 'highlight' field. This field is of the same type as the url
# field, except that it points to the 'snippet-highlight' url pattern, instead of the
# 'snippet-detail' url pattern.


# Because we've included format suffixed URLs such as '.json', we also need to indicate on the
# highlight field that any format suffixed hyperlinks it returns should use the '.html' suffix.
class SnippetSerializer(serializers.HyperlinkedModelSerializer[Snippet]):
    # We could have also used CharField(read_only=True) instead of ReadOnlyField
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(view_name="snippet-highlight", format="html")

    class Meta:
        model = Snippet
        fields = [
            "url",
            "id",
            "highlight",
            "owner",
            "title",
            "code",
            "linenos",
            "language",
            "style",
        ]


class UserSerializer(serializers.ModelSerializer[User]):
    snippets: serializers.HyperlinkedRelatedField[Snippet] = serializers.HyperlinkedRelatedField(
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = User
        # Because 'snippets' is a reverse relationship on the User model, it will not be included
        # by default when using the ModelSerializer class, so we needed to add an explicit field
        # for it.
        fields = ["url", "id", "username", "snippets"]
