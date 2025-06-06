from rest_framework import permissions

class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, а редактирование/удаление только автору или админу.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_superuser