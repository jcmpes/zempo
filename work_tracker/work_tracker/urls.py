from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🌍 Landing pública
    path('', TemplateView.as_view(template_name="landing.html"), name='landing'),

    # 🔐 Auth
    path('', include('accounts.urls')),

    # 🏢 App (tracking)
    path('app/', include('tracking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Work Tracker'
admin.site.site_title = 'Work Tracker'