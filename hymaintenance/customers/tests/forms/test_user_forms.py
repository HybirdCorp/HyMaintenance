
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ...forms import MaintenanceUserCreateForm
from ...models import MaintenanceUser


class UserCreateFormTestCase(TestCase):

    def __get_dict_for_post(self):
        return {"email": "gordon.freeman@blackmesa.com",
                "password": "azerty"}

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceUserCreateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {'email': [expected],
                                           'password': [expected]})

    def test_if_create_operator_form_works(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(
            is_superuser=False).count())
        form = MaintenanceUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(1, MaintenanceUser.objects.filter(is_superuser=False).count())
        self.assertEqual("gordon.freeman@blackmesa.com", MaintenanceUser.objects.first().email)

    def test_if_create_operator_form_works_without_commit(self):
        self.assertEqual(0, MaintenanceUser.objects.filter(
            is_superuser=False).count())
        form = MaintenanceUserCreateForm(data=self.__get_dict_for_post())
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save(False))
        self.assertEqual(0, MaintenanceUser.objects.filter(is_superuser=False).count())
