from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import Account, Organization


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Usuario",
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-800 text-lg focus:outline-none focus:ring focus:ring-blue-300",
            "autocomplete": "username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Contraseña",
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-800 text-lg focus:outline-none focus:ring focus:ring-blue-300",
            "autocomplete": "current-password"
        })
    )


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-800 text-lg focus:outline-none focus:ring focus:ring-blue-300",
            "placeholder": "Nombre de usuario"
        })
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-800 text-lg focus:outline-none focus:ring focus:ring-blue-300",
            "placeholder": "Contraseña"
        })
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-800 text-lg focus:outline-none focus:ring focus:ring-blue-300",
            "placeholder": "Confirmar contraseña"
        })
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # Validar que no exista ya
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya existe")
        return username

    def save(self, commit=True, organization=None):
        user = super().save(commit=commit)

        # Marcar usuario como staff para entrar al admin
        user.is_staff = True

        # Asignar organización
        if commit and organization:
            Account.objects.create(user=user, organization=organization)

            # Añadir permisos para ver y editar workperiods y usuarios.
            # El admin está customizado para que los usuarios staff solo
            # puedan editar los detalles de su propio usuario.
            user.user_permissions.add(25, 26, 27, 28, 14, 16)
            user.save()

        return user


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Nombre de la organización",
            })
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        slug = slugify(name)

        if Organization.objects.filter(slug=slug).exists():
            raise forms.ValidationError("Ese nombre ya está en uso")

        return name
