from io import StringIO

from high_ui.tests.utils import SetDjangoLanguage

from django.core.management import call_command
from django.test import TestCase
from django.utils.translation import gettext as _

from ..models.user import MaintenanceUser
from .factories import AdminUserFactory


class CreateAdminCommandTestCase(TestCase):
    def test_create_admin_when_no_admin_already_exists(self):
        with SetDjangoLanguage("en"):
            output = StringIO()

            call_command("create_admin", stdout=output)

            self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True).count())
            self.assertTrue(MaintenanceUser.objects.filter(email="admin@mail.com"))
            self.assertIn(_("Successfully create an admin user."), output.getvalue())

    def test_create_admin_when_one_admin_already_exists(self):
        with SetDjangoLanguage("en"):
            output = StringIO()
            AdminUserFactory()

            call_command("create_admin", stdout=output)

            self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True).count())
            self.assertFalse(MaintenanceUser.objects.filter(email="admin@mail.com"))
            self.assertIn(_("There is already one admin user."), output.getvalue())

    def test_create_admin_when_two_admins_already_exist(self):
        with SetDjangoLanguage("en"):
            output = StringIO()
            AdminUserFactory()
            AdminUserFactory()

            call_command("create_admin", stdout=output)

            self.assertEqual(2, MaintenanceUser.objects.filter(is_superuser=True).count())
            self.assertFalse(MaintenanceUser.objects.filter(email="admin@mail.com"))
            self.assertIn(_("There are already {} admin users.").format(2), output.getvalue())
