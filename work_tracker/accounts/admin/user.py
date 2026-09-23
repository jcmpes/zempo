from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from accounts.models import Account

User = get_user_model()


class CustomUserAdmin(UserAdmin):

    # Incluir Organization en list display
    def organization(self, obj):
        # obj es el User
        # Como es OneToOne, basta con acceder a obj.account
        try:
            return obj.account.organization.name
        except Account.DoesNotExist:
            return "-"

    organization.short_description = "Organización"
    organization.admin_order_field = "account__organization__name"

    def get_list_display(self, request):
        base = list(super().get_list_display(request))

        if request.user.is_superuser:
            # Añadimos la columna de organización
            if "organization" not in base:
                base.append("organization")
            return base

        # Para usuarios normales, ocultar ciertos campos
        hidden = ("is_staff", "is_superuser", "groups")
        return [f for f in base if f not in hidden]

    # Si no es superuser, no mostrar búsqueda
    def get_search_fields(self, request):
        if not request.user.is_superuser:
            return ()
        return super().get_search_fields(request)

    # Si no es superuser, no mostrar filtros en el listado
    def get_list_filter(self, request):
        if not request.user.is_superuser:
            return ()
        return super().get_list_filter(request)

    # Ocultar estas secciones para usuarios no superuser
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)

        # Usuario normal: sin grupos ni permisos
        if not request.user.account.is_org_admin:
            return (
                (None, {'fields': ('username', 'password')}),
                (
                    "Información personal",
                    {'fields': ('first_name', 'last_name', 'email')}
                ),
            )

        # Admin de organización: puede gestionar grupos/permisos
        return (
            (None, {'fields': ('username', 'password')}),
            (
                "Información personal",
                {'fields': ('first_name', 'last_name', 'email')}
            ),
            (
                "Permisos",
                {'fields': ('groups', 'user_permissions')}
            ),
        )

    def get_readonly_fields(self, request, obj=None):
        # Superuser puede editar todo
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)

        # org admin puede editar permisos y grupos
        if request.user.account.is_org_admin:
            return [
                'is_superuser',
                'is_staff',
                'is_active',
                'last_login',
                'date_joined',
            ]

        # Usuario sencillo no puede editar permisos y grupos
        return [
            'is_superuser',
            'is_staff',
            'is_active',
            'groups',
            'user_permissions',
            'last_login',
            'date_joined',
        ]

    # ✅ Qué ve cada usuario
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.account.is_org_admin:
            # Ver solo usuarios de su organización
            return qs.filter(account__organization=request.user.account.organization)

        # Usuarios normales solo ven su propio usuario
        return qs.filter(id=request.user.id)

    # ✅ Qué puede cambiar cada usuario
    def has_change_permission(self, request, obj=None):
        if obj is None:  # listado
            return True

        if request.user.is_superuser:
            return True

        if request.user.account.is_org_admin:
            return obj.account.organization == request.user.account.organization

        # Usuarios normales solo pueden editarse a sí mismos
        return obj.id == request.user.id

    # ❌ No permitir borrar usuarios si no es superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # ❌ No permitir añadir nuevos usuarios si no es superuser
    def has_add_permission(self, request):
        return request.user.is_superuser

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if (
                db_field.name == "user_permissions"
                and not request.user.is_superuser
        ):
            excluded_apps = (
                "accounts",
                "admin",
                "contenttypes",
                "sessions",
            )

            kwargs["queryset"] = Permission.objects.exclude(
                content_type__app_label__in=excluded_apps
            ).exclude(
                content_type__app_label="auth",
                codename__in=(
                    "add_group",
                    "change_group",
                    "delete_group",
                ),
            )

        return super().formfield_for_manytomany(
            db_field, request, **kwargs
        )


# Registrar
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
