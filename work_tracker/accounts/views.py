from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from .forms import UserRegistrationForm, UserLoginForm, OrganizationForm


class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {"form": form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Obtenemos la organización de la request
            # que añade nuestro middleware
            print(request.organization)
            if not request.organization:
                return render(request, 'accounts/register.html', {
                    "form": form,
                    "error": "Dominio no válido para registro"
                })

            form.save(organization=request.organization)
            return redirect('login')
        return render(request, 'accounts/register.html', {"form": form})


class CustomLoginView(LoginView):
    authentication_form = UserLoginForm
    template_name = 'accounts/login.html'


class LandingView(TemplateView):
    template_name = "landing.html"


class create_organization(View):
    def get(self, request):
        form = OrganizationForm()

        return render(request, "accounts/create_org.html", {"form": form})

    def post(self, request):
        form = OrganizationForm(request.POST)

        if form.is_valid():
            org = form.save()

            messages.success(request, "Organización creada correctamente")

            return redirect(f"https://{org.slug}.zempo.es")

        else:
            messages.error(request, "Revisa el formulario")

        return render(request, "accounts/create_org.html", {"form": form})
