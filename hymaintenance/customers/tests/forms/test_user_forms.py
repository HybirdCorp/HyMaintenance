from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ...forms import MaintenanceUserModelForm
from ...forms import MaintenanceUserProfileUpdateForm
from ...forms import ManagerUserCreateForm
from ...forms import ManagerUsersUpdateForm
from ...forms import OperatorUserArchiveForm
from ...forms import OperatorUserCreateFormWithCompany
from ...forms import OperatorUsersUpdateForm
from ...forms import OperatorUserUnarchiveForm
from ...models import MaintenanceUser
from ..factories import AdminUserFactory
from ..factories import CompanyFactory
from ..factories import ManagerUserFactory
from ..factories import OperatorUserFactory


class UserCreateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def __get_dict_for_post(self):
        return {
            "email": "gordon.freeman@blackmesa.com",
            "password1": "my safe password",
            "password2": "my safe password",
        }

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceUserModelForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"email": [expected]})

    def test_if_create_user_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter().count())
        form = MaintenanceUserModelForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter().count())
        operator = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual("gordon.freeman@blackmesa.com", operator.email)

    def test_if_create_operator_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateFormWithCompany(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        operator = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual("gordon.freeman@blackmesa.com", operator.email)
        self.assertEqual(1, operator.operator_for.all().count())

    def test_if_create_manager_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = ManagerUserCreateForm(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        manager = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual("gordon.freeman@blackmesa.com", manager.email)
        self.assertEqual(self.company, manager.company)

    def test_if_create_operator_form_works_without_commit(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateFormWithCompany(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save(False))
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())


class OperatorUserArchiveFormTestCase(TestCase):
    def setUp(self):
        self.op1 = OperatorUserFactory(
            email="chell@aperture-science.com", password="azerty", is_active=False, first_name="Chell"
        )
        self.op2 = OperatorUserFactory(
            email="gordon.freeman@blackmesa.com", password="azerty", first_name="Gordon", last_name="Freeman"
        )

    def test_archive_form_update_new_status(self):
        form = OperatorUserArchiveForm(data={"active_operators": [self.op2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertFalse(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_archive_form_dont_update_when_no_new_status(self):
        form = OperatorUserArchiveForm(data={"active_operators": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_unarchive_form_update_new_status(self):
        form = OperatorUserUnarchiveForm(data={"inactive_operators": [self.op1]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_unarchive_form_dont_update_when_no_new_status(self):
        form = OperatorUserUnarchiveForm(data={"inactive_operators": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)


class ManagerUserUpdateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.m2 = ManagerUserFactory(is_active=False, company=self.company)
        self.m1 = ManagerUserFactory(company=self.company)
        self.m3 = ManagerUserFactory(company=self.company)
        self.m4 = ManagerUserFactory(is_active=False, company=self.company)

    def test_update_form_initial_values(self):
        form = ManagerUsersUpdateForm(company=self.company)
        self.assertEqual(list(form.fields["users"].initial), [self.m1, self.m3])

    def test_update_form(self):
        form = ManagerUsersUpdateForm(company=self.company, data={"users": [self.m1, self.m2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceUser.objects.get(id=self.m2.id).is_active)
        self.assertTrue(MaintenanceUser.objects.get(id=self.m1.id).is_active)
        self.assertFalse(MaintenanceUser.objects.get(id=self.m3.id).is_active)
        self.assertFalse(MaintenanceUser.objects.get(id=self.m4.id).is_active)


class OperatorUserUpdateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

        self.op1 = OperatorUserFactory(is_active=True)
        self.op1.operator_for.add(self.company)
        self.op2 = OperatorUserFactory(is_active=True)
        self.op2.operator_for.add(self.company)

        self.op3 = OperatorUserFactory(is_active=True)
        self.op4 = OperatorUserFactory(is_active=True)

    def test_update_form_initial_values(self):
        form = OperatorUsersUpdateForm(company=self.company)
        self.assertEqual(list(form.fields["users"].initial), [self.op1, self.op2])

    def test_update_form(self):
        self.assertEqual(list(self.company.managed_by.all()), [self.op1, self.op2])
        form = OperatorUsersUpdateForm(company=self.company, data={"users": [self.op1, self.op3]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(list(self.company.managed_by.all()), [self.op1, self.op3])


class MaintenanceUserProfileUpdateFormTestCase(TestCase):
    def test_required_values(self):
        user = AdminUserFactory()
        form = MaintenanceUserProfileUpdateForm(instance=user, data={})

        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {"email": [expected], "first_name": [expected], "last_name": [expected], "confirm_password": [expected]},
        )

    def test_wrong_confirmation_password(self):
        user = AdminUserFactory(password="azerty")
        form = MaintenanceUserProfileUpdateForm(
            instance=user,
            data={
                "first_name": "Gordon",
                "last_name": "Freeman",
                "email": "gordon.freeman@blackmesa.com",
                "confirm_password": "qwerty",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {"confirm_password": [_("Invalid password.")]})

    def test_update_profil(self):
        user = AdminUserFactory(first_name="Chell", last_name="", email="chell@aperture-science.com", password="azerty")
        form = MaintenanceUserProfileUpdateForm(
            instance=user,
            data={
                "first_name": "Gordon",
                "last_name": "Freeman",
                "email": "gordon.freeman@blackmesa.com",
                "confirm_password": "azerty",
            },
        )

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(user.pk, MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").pk)
