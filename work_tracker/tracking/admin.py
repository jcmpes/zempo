from datetime import timezone as dt_timezone

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from .models import WorkPeriod
from .services.excel_export import excel_export

User = get_user_model()


class UserFilter(admin.SimpleListFilter):
    title = 'User'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        # SUPERUSER
        if request.user.is_superuser:
            return [(u.id, u.username) for u in User.objects.all()]

        # ORGANIZATION ADMIN
        if request.user.account.is_org_admin:
            org = request.user.account.organization
            users = User.objects.filter(account__organization=org)
            return [(u.id, u.username) for u in users]

        # Usuario normal → sin filtro
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset


class WorkPeriodAdmin(admin.ModelAdmin):
    list_display = ('date', 'formatted_start_time', 'formatted_end_time', 'edit_link')
    list_filter = (UserFilter,)
    date_hierarchy = 'start_time'
    actions = [excel_export]

    def username(self, obj):
        return obj.user.username

    username.short_description = "Usuario"
    username.admin_order_field = "user__username"

    def get_list_display(self, request):
        base = list(super().get_list_display(request))

        # Mostrar columna de usuario para superusers y organization admins
        if request.user.is_superuser or request.user.account.is_org_admin:
            # Insertamos al principio para mejor visibilidad
            if "username" not in base:
                base.insert(0, "username")
            return base

        # Usuario normal → sin username
        return base

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    def get_fields(self, request, obj=None):
        if obj:
            return ['start_time', 'end_time']
        return ['user', 'start_time', 'end_time']

    def edit_link(self, obj):
        url = reverse('admin:tracking_workperiod_change', args=[obj.id])
        return format_html('<a href="{}">Editar</a>', url)

    edit_link.short_description = 'Acciones'

    def date(self, obj):
        return obj.start_time.strftime("%-d de %B")

    date.short_description = 'Fecha'

    def formatted_start_time(self, obj):
        if not obj.end_time:
            return ''

        dt = obj.start_time
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, dt_timezone.utc)

        local_datetime = timezone.localtime(dt)

        return local_datetime.strftime('%H:%M')

    formatted_start_time.short_description = 'Hora de Inicio'

    def formatted_end_time(self, obj):
        if not obj.end_time:
            return ''

        dt = obj.end_time
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, dt_timezone.utc)

        local_datetime = timezone.localtime(dt)

        return local_datetime.strftime('%H:%M')

    formatted_end_time.short_description = 'Hora de Fin'

    def get_queryset(self, request):
        qs = super().get_queryset(request).order_by('start_time')

        # SUPERUSER
        if request.user.is_superuser:
            return qs.order_by('user__id', 'end_time')

        # ORGANIZATION ADMIN → work_periods de toda su organización
        if request.user.account.is_org_admin:
            org = request.user.account.organization
            return qs.filter(user__account__organization=org).order_by('user__id', 'end_time')

        # Usuario normal → solo los suyos
        return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        default_factory = super().get_form(request, obj, **kwargs)

        def factory(*args, **_kwargs):
            form = default_factory(*args, **_kwargs)
            return self.modify_form(form, request, obj)

        return factory

    @staticmethod
    def modify_form(form, request, obj):
        form.initial['user'] = request.user.id
        if not request.user.is_superuser and form.fields.get('user'):
            form.fields['user'].widget = form.fields['user'].hidden_widget()
        return form


admin.site.register(WorkPeriod, WorkPeriodAdmin)
