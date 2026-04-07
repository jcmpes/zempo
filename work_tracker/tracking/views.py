from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime

from .models import WorkPeriod


@login_required
def home(request):
    user_id = request.user.id
    total_seconds_today = get_total_seconds_worked_today(user_id)

    active_period = WorkPeriod.objects.filter(user=request.user,
                                              organization=request.organization,
                                              end_time__isnull=True).first()

    if request.method == "POST":
        if active_period:
            # Detener el periodo activo
            active_period.end_time = now()
            active_period.save()
        else:
            # Crear un nuevo periodo
            WorkPeriod.objects.create(user=request.user, organization=request.organization)

        return redirect('home')

    # Si hay un periodo activo, pasamos el tiempo de inicio al cliente en ISO 8601 sin microsegundos
    active_period_start_time = localtime(active_period.start_time).replace(
        microsecond=0).isoformat() if active_period else None
    context = {
        'total_seconds_today': total_seconds_today,
        'active_period_start_time': active_period_start_time
    }
    return render(request, 'tracking/home.html', context)


def get_total_seconds_worked_today(user_id):
    today = now().date().isoformat()
    # Filtramos los periodos trabajados hoy
    today_work_periods = WorkPeriod.objects.filter(
        user_id=user_id,
        start_time__date=today,
    )
    if not today_work_periods:
        today_work_periods = WorkPeriod.objects.filter(
            user_id=user_id,
            end_time__isnull=True,
        )
    # Sumar manualmente el tiempo trabajado hoy
    total_seconds = timedelta()
    for period in today_work_periods:
        if period.end_time:
            total_seconds += period.end_time - period.start_time
        else:
            total_seconds += now() - period.start_time
    # Pasar los segundos totales
    total_seconds_today = total_seconds.total_seconds()
    return total_seconds_today


@login_required
def get_total_seconds_today(request):
    user_id = request.user.id
    total_seconds_today = get_total_seconds_worked_today(user_id)
    return JsonResponse({
        'total_seconds_today': total_seconds_today
    })
