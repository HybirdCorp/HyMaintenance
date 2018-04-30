
from django.test import TestCase

from ...models import MaintenanceUser


class MaintenanceUserTestCase(TestCase):

    def test___create_user(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(
            is_superuser=False).count())
        MaintenanceUser.objects._create_user("gordon.freeman@blackmesa.com",
                                             "azerty",
                                             True,
                                             False,
                                             first_name="Gordon",
                                             last_name="Freeman")
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual("Gordon", MaintenanceUser.objects.first().first_name)

    def test___create_user_required_email(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(
            is_superuser=False).count())
        self.assertRaises(ValueError, MaintenanceUser.objects._create_user, email="",
                          password="azerty", is_staff=True, is_superuser=False)

    def test___create_user_without_commit_in_bd(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(
            is_superuser=False).count())
        MaintenanceUser.objects._create_user("gordon.freeman@blackmesa.com",
                                             "azerty",
                                             True,
                                             False,
                                             first_name="Gordon",
                                             last_name="Freeman")
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual("Gordon", MaintenanceUser.objects.first().first_name)

    def test_i_can_create_a_maintenance_user(self):
        MaintenanceUser.objects.create_user("gordon.freeman@blackmesa.com",
                                            "azerty",
                                            first_name="Gordon",
                                            last_name="Freeman")
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())

    def test_i_can_create_a_maintenance_superuser(self):
        MaintenanceUser.objects.create_superuser("gordon.freeman@blackmesa.com",
                                                 "azerty",
                                                 first_name="Gordon",
                                                 last_name="Freeman")
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True).count())

    def test_get_operator_by_primary_key(self):
        self.assertEqual(0, MaintenanceUser.objects.all().count())
        user = MaintenanceUser.objects._create_user("gordon.freeman@blackmesa.com",
                                                    "azerty",
                                                    True,
                                                    False,
                                                    first_name="Gordon",
                                                    last_name="Freeman")
        self.assertEqual(user, MaintenanceUser.objects.get_by_primary_key(1))
