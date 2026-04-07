from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseNotFound
from django.shortcuts import redirect


class OrganizationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.organization = None

        host = request.get_host().split(':')[0].lower()

        if host.endswith("localhost") or host.endswith("127.0.0.1"):
            parts = host.split(".")

            if len(parts) == 2:
                subdomain = parts[0]
            else:
                return self.get_response(request)
        else:
            parts = host.split('.')

            # Root domain
            if len(parts) < 3:
                return self.get_response(request)

            # Subdomain → multi-tenant
            subdomain = parts[0]

        from accounts.models import Organization

        try:
            request.organization = Organization.objects.get(slug=subdomain)
            # Redirect to home
            if request.organization and request.path == '/':
                if request.user.is_authenticated:
                    return redirect('home')
                return redirect('login')
        except Organization.DoesNotExist:
            return HttpResponseNotFound("Organización no encontrada")

        # User security
        if request.user.is_authenticated:
            account = getattr(request.user, 'account', None)

            if not account or account.organization != request.organization:
                logout(request)
                return redirect('login')

        return self.get_response(request)
