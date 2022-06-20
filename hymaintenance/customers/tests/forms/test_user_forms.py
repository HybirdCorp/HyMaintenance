from customers.forms.users.create_user import AdminUserCreateForm
from customers.forms.users.create_user import ManagerUserCreateForm
from customers.forms.users.create_user import OperatorUserCreateForm
from customers.forms.users.create_user import OperatorUserCreateFormWithCompany
from customers.forms.users.update_user import AdminUserUpdateForm
from customers.forms.users.update_user import OperatorUserUpdateForm
from customers.forms.users.user_base import MaintenanceUserCreateForm
from customers.forms.users.user_base import MaintenanceUserModelForm
from customers.forms.users.user_profile import MaintenanceUserProfileUpdateForm
from customers.forms.users.user_profile import StaffUserProfileUpdateForm
from customers.forms.users_list.list import OperatorUsersListArchiveForm
from customers.forms.users_list.list import OperatorUsersListUnarchiveForm
from customers.forms.users_list.list_by_company import ManagerUsersListUpdateForm
from customers.forms.users_list.list_by_company import OperatorUsersListUpdateForm
from maintenance.models import MaintenanceConsumer

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ...models import MaintenanceUser
from ..factories import AdminUserFactory
from ..factories import CompanyFactory
from ..factories import ManagerUserFactory
from ..factories import OperatorUserFactory


class UserCreateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()
        cls.email = "gordon.freeman@blackmesa.com"
        cls.password = "my safe password"

    def __get_dict_for_post(self):
        return {
            "first_name": "Gordon",
            "last_name": "Freeman",
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        }

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceUserModelForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"email": [expected], "first_name": [expected], "last_name": [expected]})

    def test_password_mismatch_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["password2"] = "my password"
        form = MaintenanceUserCreateForm(data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual([_("The two password fields didn't match.")], form.errors["password2"])

    def test_when_one_password_is_missing(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["password1"] = None
        form = MaintenanceUserCreateForm(data=dict_for_post)
        self.assertFalse(form.is_valid())

    def test_if_create_maintenance_user_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter().count())
        form = MaintenanceUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter().count())
        user = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual(self.email, user.email)
        self.assertTrue(user.check_password(self.password))

    def test_if_create_manager_form_works(self):
        dic_for_post = self.__get_dict_for_post()
        dic_for_post["create_consumer"] = False
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())

        form = ManagerUserCreateForm(company=self.company, data=dic_for_post)

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        manager = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual(self.email, manager.email)
        self.assertTrue(manager.check_password(self.password))
        self.assertEqual(0, MaintenanceConsumer.objects.all().count())

    def test_if_create_manager_form_works__create_consumer(self):
        dic_for_post = self.__get_dict_for_post()
        dic_for_post["create_consumer"] = True
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual(0, MaintenanceConsumer.objects.all().count())

        form = ManagerUserCreateForm(company=self.company, data=dic_for_post)

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        manager = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual(self.email, manager.email)
        self.assertTrue(manager.check_password(self.password))
        consumers = MaintenanceConsumer.objects.all()
        self.assertEqual(1, consumers.count())
        consumer = consumers.first()
        self.assertEqual("Gordon Freeman", consumer.name)

    def test_if_create_operator_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        operator = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual(self.email, operator.email)
        self.assertTrue(operator.check_password(self.password))

    def test_if_create_operator_with_company_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateFormWithCompany(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        operator = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual(self.email, operator.email)
        self.assertTrue(operator.check_password(self.password))
        self.assertEqual(1, operator.operator_for.all().count())

    def test_if_create_admin_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = AdminUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=True).count())
        admin = MaintenanceUser.objects.filter(is_superuser=True).first()
        self.assertEqual(self.email, admin.email)
        self.assertTrue(admin.check_password(self.password))

    def test_if_create_operator_form_works_without_commit(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateFormWithCompany(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save(False))
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())


class UserUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()
        cls.admin = AdminUserFactory(email="wheatley@aperture-science.com")
        cls.operator = OperatorUserFactory(email="glados@aperture-science.com")
        cls.manager = ManagerUserFactory(email="chell@aperture-science.com")
        cls.email = "gordon.freeman@blackmesa.com"
        cls.password = "my safe password"

    def __get_dict_for_post(self):
        return {"first_name": "Gordon", "last_name": "Freeman", "email": self.email}

    def test_if_update_maintenance_user_form_works(self):
        form = MaintenanceUserModelForm(instance=self.manager, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        user = MaintenanceUser.objects.get(pk=self.manager.pk)
        self.assertEqual(self.email, user.email)

    def test_if_update_operator_user_form_works(self):
        form = OperatorUserUpdateForm(instance=self.operator, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        user = MaintenanceUser.objects.get(pk=self.operator.pk)
        self.assertEqual(self.email, user.email)

    def test_if_update_admin_user_form_works(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["is_staff"] = True
        form = AdminUserUpdateForm(instance=self.admin, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        user = MaintenanceUser.objects.get(pk=self.admin.pk)
        self.assertEqual(self.email, user.email)
        self.assertTrue(user.is_staff)


class OperatorUsersListArchiveFormTestCase(TestCase):
    def setUp(self):
        self.op1 = OperatorUserFactory(
            email="chell@aperture-science.com", password="azerty", is_active=False, first_name="Chell"
        )
        self.op2 = OperatorUserFactory(
            email="gordon.freeman@blackmesa.com", password="azerty", first_name="Gordon", last_name="Freeman"
        )

    def test_archive_form_update_new_status(self):
        form = OperatorUsersListArchiveForm(data={"active_users": [self.op2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertFalse(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_archive_form_dont_update_when_no_new_status(self):
        form = OperatorUsersListArchiveForm(data={"active_users": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_unarchive_form_update_new_status(self):
        form = OperatorUsersListUnarchiveForm(data={"inactive_users": [self.op1]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)

    def test_unarchive_form_dont_update_when_no_new_status(self):
        form = OperatorUsersListUnarchiveForm(data={"inactive_users": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(MaintenanceUser.objects.get(email="chell@aperture-science.com").is_active)
        self.assertTrue(MaintenanceUser.objects.get(email="gordon.freeman@blackmesa.com").is_active)


class ManagerUsersUpdateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.m2 = ManagerUserFactory(is_active=False, company=self.company)
        self.m1 = ManagerUserFactory(company=self.company, first_name="Chell")
        self.m3 = ManagerUserFactory(company=self.company, first_name="Glados")
        self.m4 = ManagerUserFactory(is_active=False, company=self.company)

    def test_update_form_initial_values(self):
        form = ManagerUsersListUpdateForm(company=self.company)
        self.assertEqual(list(form.fields["users"].initial), [self.m1, self.m3])

    def test_update_form(self):
        form = ManagerUsersListUpdateForm(company=self.company, data={"users": [self.m1, self.m2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceUser.objects.get(id=self.m2.id).is_active)
        self.assertTrue(MaintenanceUser.objects.get(id=self.m1.id).is_active)
        self.assertFalse(MaintenanceUser.objects.get(id=self.m3.id).is_active)
        self.assertFalse(MaintenanceUser.objects.get(id=self.m4.id).is_active)


class OperatorUsersUpdateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

        self.op1 = OperatorUserFactory(is_active=True, first_name="Gordon")
        self.op1.operator_for.add(self.company)
        self.op2 = OperatorUserFactory(is_active=True, first_name="Chell")
        self.op2.operator_for.add(self.company)

        self.op3 = OperatorUserFactory(is_active=True, first_name="Glados")
        self.op4 = OperatorUserFactory(is_active=True, first_name="Wheatley")

    def test_update_form_initial_values(self):
        form = OperatorUsersListUpdateForm(company=self.company)
        self.assertEqual(list(form.fields["users"].initial), [self.op2, self.op1])

    def test_update_form(self):
        self.assertEqual(list(self.company.managed_by.all().order_by("first_name")), [self.op2, self.op1])
        form = OperatorUsersListUpdateForm(company=self.company, data={"users": [self.op1, self.op3]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(list(self.company.managed_by.all().order_by("first_name")), [self.op3, self.op1])


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

    def test_maintenance_user_update_profil(self):
        user = ManagerUserFactory(
            first_name="Chell", last_name="", email="chell@aperture-science.com", password="azerty"
        )
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

    def test_staff_user_update_profil(self):
        user = AdminUserFactory(first_name="Chell", last_name="", email="chell@aperture-science.com", password="azerty")
        form = StaffUserProfileUpdateForm(
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
