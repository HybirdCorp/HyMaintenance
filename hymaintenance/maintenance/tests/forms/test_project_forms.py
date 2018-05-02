import datetime

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from customers.models import Company
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.forms import INACTIF_CONTRACT_INPUT, ProjectCreateForm, ProjectUpdateForm
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME, CONSUMMED_TOTAL_TIME

from ..factories import create_project


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
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {'company_name': [expected],
                                           'contract1_counter_name': [expected],
                                           'contract2_counter_name': [expected],
                                           'contract3_counter_name': [expected],
                                           'contract1_date': [expected],
                                           'contract2_date': [expected],
                                           'contract3_date': [expected],
                                           'contract1_visible': [expected],
                                           'contract2_visible': [expected],
                                           'contract3_visible': [expected],
                                           'contract1_total_type': [expected],
                                           'contract2_total_type': [expected],
                                           'contract3_total_type': [expected],
                                           'contract1_number_hours': [expected],
                                           'contract2_number_hours': [expected],
                                           'contract3_number_hours': [expected]})

    def test_valid_form_create_a_company(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())

    def test_valid_form_create_a_support_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count())

    def test_valid_form_create_a_maintenance_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract2_visible"] = 1
        dict_for_post["contract2_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=2, disabled=False).count())

    def test_valid_form_add_all_operators_to_company(self):
        MaintenanceUserFactory(email="gordon.freeman2@blackmesa.com",
                               password="azerty")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")
        self.assertEqual(2, company.managed_by.all().count())

    def test_create_company_and_contracts_with_operator_args_add_only_one_operator(self):
        user2 = MaintenanceUserFactory(email="gordon.freeman2@blackmesa.com",
                                       password="azerty")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        form.is_valid()
        form.create_company_and_contracts(operator=user2)
        company = Company.objects.get(name="Black Mesa")
        self.assertEqual([user2], list(company.managed_by.all()))

    def test_valid_form_create_a_correction_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract3_visible"] = 1
        dict_for_post["contract3_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=3, disabled=False).count())

    def test_valid_form_create_a_company_and_invisible_available_time_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        dict_for_post["contract1_visible"] = 0
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = 80

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, visible=False, total_type=AVAILABLE_TOTAL_TIME, number_hours=80, disabled=False).count())

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
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors['contract1_number_hours'], [expected])


class ProjectUpdateFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.company, cls.contract1, cls.contract2, cls.contract3 = create_project()

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

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = ProjectUpdateForm(company=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {'company_name': [expected],
                                           'contract1_counter_name': [expected],
                                           'contract2_counter_name': [expected],
                                           'contract3_counter_name': [expected],
                                           'contract1_date': [expected],
                                           'contract2_date': [expected],
                                           'contract3_date': [expected],
                                           'contract1_visible': [expected],
                                           'contract2_visible': [expected],
                                           'contract3_visible': [expected],
                                           'contract1_total_type': [expected],
                                           'contract2_total_type': [expected],
                                           'contract3_total_type': [expected],
                                           'contract1_number_hours': [expected],
                                           'contract2_number_hours': [expected],
                                           'contract3_number_hours': [expected]})

    def test_valid_form_update_a_company(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())

    def test_valid_form_update_a_support_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count())

    def test_valid_form_update_a_maintenance_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        dict_for_post["contract2_visible"] = 1
        dict_for_post["contract2_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=2, disabled=False).count())

    def test_valid_form_update_a_correction_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        dict_for_post["contract3_visible"] = 1
        dict_for_post["contract3_total_type"] = CONSUMMED_TOTAL_TIME

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=3, disabled=False).count())

    def test_valid_form_update_a_company_and_invisible_available_time_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        dict_for_post["contract1_visible"] = 0
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = 80

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, visible=False, total_type=AVAILABLE_TOTAL_TIME, number_hours=80, disabled=False).count())

    def test_invalid_form_update_already_existing_company(self):
        CompanyFactory.create(name="Black Mesa")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['company_name'].as_text(), "* " + str(_("This company already exists")))

    def test_when_i_bound_a_update_form_with_under_min_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = -10
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _('Ensure this value is greater than or equal to %(limit_value)s.') % {'limit_value': 0}
        self.assertEqual(form.errors['contract1_number_hours'].as_text(), "* %s" % expected)

    def test_when_i_bound_a_update_form_with_string_as_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = "I'm a duration"
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors['contract1_number_hours'], [expected])
