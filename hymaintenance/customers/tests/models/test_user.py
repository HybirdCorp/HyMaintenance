from django.test import TestCase

from ...models import MaintenanceUser
from ..factories import AdminOperatorUserFactory
from ..factories import AdminUserFactory
from ..factories import ManagerUserFactory
from ..factories import OperatorUserFactory


class MaintenanceUserTestCase(TestCase):
    def test___create_user(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        MaintenanceUser.objects._create_user(
            "gordon.freeman@blackmesa.com", "azerty", True, False, first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual("Gordon", MaintenanceUser.objects.first().first_name)

    def test___create_user_required_email(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertRaises(
            ValueError,
            MaintenanceUser.objects._create_user,
            email="",
            password="azerty",
            is_staff=True,
            is_superuser=False,
        )

    def test___create_user_without_commit_in_bd(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        MaintenanceUser.objects._create_user(
            "gordon.freeman@blackmesa.com", "azerty", True, False, first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual("Gordon", MaintenanceUser.objects.first().first_name)

    def test_i_can_create_a_operator_user(self):
        MaintenanceUser.objects.create_operator_user(
            "gordon.freeman@blackmesa.com", "azerty", first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())

    def test_i_can_create_a_manager_user(self):
        MaintenanceUser.objects.create_manager_user(
            "gordon.freeman@blackmesa.com", "azerty", first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())

    def test_i_can_create_an_admin_user(self):
        MaintenanceUser.objects.create_admin_user(
            "gordon.freeman@blackmesa.com", "azerty", first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True, is_staff=False).count())

    def test_i_can_create_an_admin_operator_user(self):
        MaintenanceUser.objects.create_admin_operator_user(
            "gordon.freeman@blackmesa.com", "azerty", first_name="Gordon", last_name="Freeman"
        )
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True, is_staff=True).count())

    def test_get_operator_by_primary_key(self):
        self.assertEqual(0, MaintenanceUser.objects.all().count())
        user = MaintenanceUser.objects._create_user(
            "gordon.freeman@blackmesa.com", "azerty", True, False, first_name="Gordon", last_name="Freeman", pk=42
        )
        self.assertEqual(user, MaintenanceUser.objects.get_by_primary_key(42))

    def test_get_admin_users_queryset(self):
        user = AdminUserFactory()
        OperatorUserFactory()
        ManagerUserFactory()
        self.assertEqual(1, MaintenanceUser.objects.get_admin_users_queryset().count())
        self.assertEqual(user.pk, MaintenanceUser.objects.get_admin_users_queryset().first().pk)

    def test_get_operator_users_queryset(self):
        AdminUserFactory()
        operator = OperatorUserFactory()
        ManagerUserFactory()
        self.assertEqual([operator], list(MaintenanceUser.objects.get_operator_users_queryset()))

    def test_get_active_operator_users_queryset(self):
        admin = AdminUserFactory(is_active=True)
        operator = OperatorUserFactory(is_active=True)
        OperatorUserFactory(is_active=False)
        ManagerUserFactory()
        self.assertNotIn(admin, list(MaintenanceUser.objects.get_active_operator_users_queryset()))
        self.assertIn(operator, list(MaintenanceUser.objects.get_active_operator_users_queryset()))

    def test_get_all_types_operator_users_queryset(self):
        AdminUserFactory()
        adminOp = AdminOperatorUserFactory()
        operator = OperatorUserFactory()
        ManagerUserFactory()
        operators = list(MaintenanceUser.objects.get_all_types_operator_users_queryset())
        self.assertEqual(2, len(operators))
        self.assertIn(operator, operators)
        self.assertIn(adminOp, operators)

    def test_get_active_all_types_operator_users_queryset(self):
        AdminUserFactory()
        adminOp = AdminOperatorUserFactory()
        op1 = OperatorUserFactory()
        OperatorUserFactory(is_active=False)
        ManagerUserFactory()
        operators = list(MaintenanceUser.objects.get_active_all_types_operator_users_queryset())
        self.assertEqual(2, len(operators))
        self.assertIn(op1, operators)
        self.assertIn(adminOp, operators)

    def test_get_manager_users_queryset(self):
        AdminUserFactory()
        OperatorUserFactory()
        manager = ManagerUserFactory()
        self.assertEqual([manager], list(MaintenanceUser.objects.get_manager_users_queryset()))

    def test_get_active_manager_users_queryset(self):
        AdminUserFactory()
        OperatorUserFactory()
        manager = ManagerUserFactory(is_active=True)
        ManagerUserFactory(is_active=False)
        self.assertEqual([manager], list(MaintenanceUser.objects.get_active_manager_users_queryset()))

    def test_has_operator_permissions(self):
        admin = AdminUserFactory()
        adminOp = AdminOperatorUserFactory()
        operator = OperatorUserFactory()
        manager = ManagerUserFactory()

        self.assertFalse(admin.has_operator_permissions())
        self.assertTrue(adminOp.has_operator_permissions())
        self.assertTrue(operator.has_operator_permissions())
        self.assertFalse(manager.has_operator_permissions())

    def test_has_admin_permissions(self):
        admin = AdminUserFactory()
        adminOp = AdminOperatorUserFactory()
        operator = OperatorUserFactory()
        manager = ManagerUserFactory()

        self.assertTrue(admin.has_admin_permissions())
        self.assertTrue(adminOp.has_admin_permissions())
        self.assertFalse(operator.has_admin_permissions())
        self.assertFalse(manager.has_admin_permissions())

    def test_has_operator_or_admin_permissions(self):
        admin = AdminUserFactory()
        adminOp = AdminOperatorUserFactory()
        operator = OperatorUserFactory()
        manager = ManagerUserFactory()

        self.assertTrue(admin.has_operator_or_admin_permissions())
        self.assertTrue(adminOp.has_operator_or_admin_permissions())
        self.assertTrue(operator.has_operator_or_admin_permissions())
        self.assertFalse(manager.has_operator_or_admin_permissions())
