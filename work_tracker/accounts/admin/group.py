from django.contrib import admin
from django.contrib.admin.sites import NotRegistered

from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin


class CustomGroupAdmin(GroupAdmin):
    """
    Solo superuser puede modificar grupos
    """
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Registrar
try:
    admin.site.unregister(Group)
except NotRegistered:
    pass

admin.site.register(Group, CustomGroupAdmin)