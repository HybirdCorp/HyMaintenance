import datetime

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from customers.models import Company
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.forms import INACTIF_CONTRACT_INPUT, ProjectCreateForm
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME, CONSUMMED_TOTAL_TIME


class ProjectCreateFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")

    def __get_dict_for_post(self):
        return {"company_name": "Black Mesa",
                "contract1_visible": INACTIF_CONTRACT_INPUT,
                "contract1_total_type": 0,
                "contract1_number_hours": 0,
                "contract1_date": datetime.date.today(),
                "contract1_counter_name": "Maintenance",
                "contract2_visible": INACTIF_CONTRACT_INPUT,
                "contract2_total_type": 0,
                "contract2_number_hours": 0,
                "contract2_date": datetime.date.today(),
                "contract2_counter_name": "Support",
                "contract3_visible": INACTIF_CONTRACT_INPUT,
                "contract3_total_type": 0,
                "contract3_number_hours": 0,
                "contract3_date": datetime.date.today(),
                "contract3_counter_name": "Corrective"}

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = ProjectCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(16, len(form.errors))
        self.assertEqual(form.errors['company_name'][0], form.fields['company_name'].error_messages['required'])
        self.assertEqual(form.errors['contract1_counter_name'][0], form.fields['contract1_counter_name'].error_messages['required'])
        self.assertEqual(form.errors['contract2_counter_name'][0], form.fields['contract2_counter_name'].error_messages['required'])
        self.assertEqual(form.errors['contract3_counter_name'][0], form.fields['contract3_counter_name'].error_messages['required'])
        self.assertEqual(form.errors['contract1_date'][0], form.fields['contract1_date'].error_messages['required'])
        self.assertEqual(form.errors['contract2_date'][0], form.fields['contract2_date'].error_messages['required'])
        self.assertEqual(form.errors['contract3_date'][0], form.fields['contract3_date'].error_messages['required'])
        self.assertEqual(form.errors['contract1_visible'][0], form.fields['contract1_visible'].error_messages['required'])
        self.assertEqual(form.errors['contract2_visible'][0], form.fields['contract2_visible'].error_messages['required'])
        self.assertEqual(form.errors['contract3_visible'][0], form.fields['contract3_visible'].error_messages['required'])
        self.assertEqual(form.errors['contract1_total_type'][0], form.fields['contract1_total_type'].error_messages['required'])
        self.assertEqual(form.errors['contract2_total_type'][0], form.fields['contract2_total_type'].error_messages['required'])
        self.assertEqual(form.errors['contract3_total_type'][0], form.fields['contract3_total_type'].error_messages['required'])
        self.assertEqual(form.errors['contract1_number_hours'][0], form.fields['contract1_number_hours'].error_messages['required'])
        self.assertEqual(form.errors['contract2_number_hours'][0], form.fields['contract2_number_hours'].error_messages['required'])
        self.assertEqual(form.errors['contract3_number_hours'][0], form.fields['contract3_number_hours'].error_messages['required'])

    def test_valid_form_create_a_company(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)
        is_valid = form.is_valid()
        form.save_company_and_contracts()

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())

    def test_valid_form_create_a_support_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.save_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1).count())

    def test_valid_form_create_a_maintenance_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract2_visible"] = 1
        dict_for_post["contract2_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.save_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=2).count())

    def test_valid_form_create_a_correction_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract3_visible"] = 1
        dict_for_post["contract3_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.save_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=3).count())

    def test_valid_form_create_a_company_and_invisible_available_time_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract1_visible"] = 0
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = 80

        is_valid = form.is_valid()
        form.save_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, visible=False, total_type=AVAILABLE_TOTAL_TIME, number_hours=80).count())

    def test_invalid_form_create_already_existing_company(self):
        CompanyFactory.create(name="Black Mesa")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['company_name'].as_text(), "* " + str(_("This company already exists")))

    def test_when_i_bound_a_create_form_with_under_min_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = -10
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _('Ensure this value is greater than or equal to %(limit_value)s.') % {'limit_value': 0}
        self.assertEqual(form.errors['contract1_number_hours'].as_text(), "* %s" % expected)

    def test_when_i_bound_a_create_form_with_string_as_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = "I'm a duration"
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['contract1_number_hours'][0], form.fields['contract1_number_hours'].error_messages['invalid'])
