
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ...forms import MaintenanceUserCreateForm, ManagerUserCreateForm, OperatorUserCreateForm
from ...models import MaintenanceUser
from ..factories import CompanyFactory


class UserCreateFormTestCase(TestCase):

    def setUp(self):
        self.company = CompanyFactory()

    def __get_dict_for_post(self):
        return {"email": "gordon.freeman@blackmesa.com",
                "password": "azerty"}

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceUserCreateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {'email': [expected],
                                           'password': [expected]})

    def test_if_create_user_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter().count())
        form = MaintenanceUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter().count())
        operator = MaintenanceUser.objects.filter(is_superuser=False).first()
        self.assertEqual("gordon.freeman@blackmesa.com", operator.email)

    def test_if_create_operator_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
        form = OperatorUserCreateForm(company=self.company, data=self.__get_dict_for_post())
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
        form = OperatorUserCreateForm(company=self.company, data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save(False))
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
