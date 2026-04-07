from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página principal
    path('get-total-seconds-today/', views.get_total_seconds_today, name='get-total-seconds-today')
]
