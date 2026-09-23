from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, Organization

User = get_user_model()


class OrganizationAdminSecurityTests(TestCase):

    def setUp(self):
        # Organizaciones
        self.org1 = Organization.objects.create(
            name="Organización 1"
        )
        self.org2 = Organization.objects.create(
            name="Organización 2"
        )

        # Grupo admins
        self.admins_group = Group.objects.get_or_create(name="organization_admin")

        # Admin de org1
        self.org1_admin = User.objects.create_user(
            username="org1_admin",
            password="password",
        )

        self.org1_admin.groups.add(self.admins_group[0])

        Account.objects.create(
            user=self.org1_admin,
            organization=self.org1,
        )

        # Usuario de org2
        self.org2_user = User.objects.create_user(
            username="org2_user",
            password="password",
        )

        Account.objects.create(
            user=self.org2_user,
            organization=self.org2,
        )

        # Grupo global
        self.global_group = Group.objects.create(
            name="Managers",
        )

        # El usuario de org2 pertenece al grupo
        self.org2_user.groups.add(self.global_group)

        self.client.force_login(self.org1_admin)

    def test_org_admin_cannot_access_group_admin(self):
        """
        Un admin de organización no debe poder administrar
        los grupos globales.
        """
        response = self.client.get(
            reverse("admin:auth_group_changelist")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_org_admin_cannot_change_global_group(self):
        """
        Un admin de org1 no puede modificar un Group global
        que también utiliza un usuario de org2.
        """
        response = self.client.post(
            reverse(
                "admin:auth_group_change",
                args=[self.global_group.pk],
            ),
            {
                "name": "Managers modificados",
            },
        )

        self.global_group.refresh_from_db()

        self.assertEqual(
            self.global_group.name,
            "Managers",
        )

    def test_org_admin_cannot_delete_global_group(self):
        """
        Un admin de org1 no puede eliminar un Group global.
        """
        group_pk = self.global_group.pk

        response = self.client.post(
            reverse(
                "admin:auth_group_delete",
                args=[group_pk],
            ),
            {
                "post": "yes",
            },
        )

        self.assertTrue(
            Group.objects.filter(pk=group_pk).exists()
        )

    def test_org2_user_remains_in_global_group(self):
        """
        Como consecuencia de lo anterior, el usuario de org2
        sigue teniendo su pertenencia al grupo.
        """
        self.assertTrue(
            self.org2_user.groups.filter(
                pk=self.global_group.pk
            ).exists()
        )