from django.views.generic import View
from rest_framework import permissions
from rest_framework.request import Request

from .models import Snippet


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to make all code snippets to be visible to anyone,
    but only allow owner of an object to edit it.
    """

    def has_object_permission(self, request: Request, view: View, obj: Snippet) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
