# from rest_framework.permissions import BasePermission


# class IsOwnerOrAssistantReadOnly(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Allow full access to the lawyer
#         if obj.user == request.user:
#             return True
#         # Allow read-only access to assistants
#         if request.user.role == 'assistant' and obj.user == request.user.parent_user:
#             return request.method in ['GET', 'HEAD', 'OPTIONS']
#         return False

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAssistantReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Traverse to the owning lawyer (user)
        owner = obj.case.client.user

        # Allow all actions if the user is the lawyer
        if owner == request.user:
            return True

        # Allow read-only actions for assistant if they belong to that lawyer
        if request.user.role == 'assistant' and request.user.parent_user == owner:
            return request.method in SAFE_METHODS  # ['GET', 'HEAD', 'OPTIONS']

        return False
