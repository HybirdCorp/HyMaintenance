import datetime

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from customers.models import Company
from customers.tests.factories import CompanyFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.forms.project import INACTIF_CONTRACT_INPUT
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceType
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME

from ..factories import create_project


class ProjectCreateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

    def __get_dict_for_post(self):
        maintenance_types = MaintenanceType.objects.order_by("id")
        return {
            "company_name": "Black Mesa",
            "contract1_visible": INACTIF_CONTRACT_INPUT,
            "contract1_total_type": 0,
            "contract1_number_hours": 0,
            "contract1_date": datetime.date.today(),
            "contract1_counter_name": maintenance_types[0].name,
            "contract2_visible": INACTIF_CONTRACT_INPUT,
            "contract2_total_type": 0,
            "contract2_number_hours": 0,
            "contract2_date": datetime.date.today(),
            "contract2_counter_name": maintenance_types[1].name,
            "contract3_visible": INACTIF_CONTRACT_INPUT,
            "contract3_total_type": 0,
            "contract3_number_hours": 0,
            "contract3_date": datetime.date.today(),
            "contract3_counter_name": maintenance_types[2].name,
        }

    def test_create_form_maintenance_type_initial_values(self):
        form = ProjectCreateForm(initial={"test": "initial not empty"})
        maintenance_types = MaintenanceType.objects.order_by("id")
        self.assertEqual(
            maintenance_types[0].name,
            form.get_initial_for_field(form.fields["contract1_counter_name"], "contract1_counter_name"),
        )
        self.assertEqual(
            maintenance_types[1].name,
            form.get_initial_for_field(form.fields["contract2_counter_name"], "contract2_counter_name"),
        )
        self.assertEqual(
            maintenance_types[2].name,
            form.get_initial_for_field(form.fields["contract3_counter_name"], "contract3_counter_name"),
        )

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = ProjectCreateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "company_name": [expected],
                "contract1_counter_name": [expected],
                "contract2_counter_name": [expected],
                "contract3_counter_name": [expected],
                "contract1_date": [expected],
                "contract2_date": [expected],
                "contract3_date": [expected],
                "contract1_visible": [expected],
                "contract2_visible": [expected],
                "contract3_visible": [expected],
                "contract1_total_type": [expected],
                "contract2_total_type": [expected],
                "contract3_total_type": [expected],
                "contract1_number_hours": [expected],
                "contract2_number_hours": [expected],
                "contract3_number_hours": [expected],
            },
        )

    def test_form_not_valid_when_no_contract(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertFalse(is_valid)
        self.assertDictEqual(form.errors, {'__all__': [_("You have to create at least one contract on the project.")]})

    def test_valid_form_create_a_support_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_create_a_maintenance_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract2_visible"] = 1
        dict_for_post["contract2_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=2, disabled=False).count()
        )

    def test_valid_form_create_contracts_counter_name(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract2_visible"] = 1
        dict_for_post["contract3_visible"] = 1
        dict_for_post["contract1_counter_name"] = "Reduice"
        dict_for_post["contract2_counter_name"] = "Reuse"
        dict_for_post["contract3_counter_name"] = "Recycle"
        form = ProjectCreateForm(data=dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, counter_name="Reduice").count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, counter_name="Reuse").count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, counter_name="Recycle").count())

    def test_valid_form_add_all_operators_to_company(self):
        OperatorUserFactory(email="gordon.freeman2@blackmesa.com", password="azerty")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")
        self.assertEqual(2, company.managed_by.all().count())

    def test_create_company_and_contracts_with_operator_args_add_only_one_operator(self):
        user2 = OperatorUserFactory(email="gordon.freeman2@blackmesa.com", password="azerty")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        form.is_valid()
        form.create_company_and_contracts(operator=user2)
        company = Company.objects.get(name="Black Mesa")
        self.assertEqual([user2], list(company.managed_by.all()))

    def test_valid_form_create_a_correction_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract3_visible"] = 1
        dict_for_post["contract3_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=3, disabled=False).count()
        )

    def test_valid_form_create_a_company_and_invisible_available_time_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 0
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = 80
        form = ProjectCreateForm(data=dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1,
            MaintenanceContract.objects.filter(
                company_id=company,
                maintenance_type_id=1,
                visible=False,
                total_type=AVAILABLE_TOTAL_TIME,
                number_hours=80,
                disabled=False,
            ).count(),
        )

    def test_invalid_form_create_already_existing_company(self):
        CompanyFactory.create(name="Black Mesa")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors["company_name"].as_text(), "* " + str(_("This company already exists.")))

    def test_when_i_bound_a_create_form_with_under_min_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = -10
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 0}
        self.assertEqual(form.errors["contract1_number_hours"].as_text(), "* %s" % expected)

    def test_when_i_bound_a_create_form_with_string_as_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = "I'm a duration"
        form = ProjectCreateForm(data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["contract1_number_hours"], [expected])

    def test_when_i_send_a_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contact"] = operator.pk
        dict_for_post["contract1_visible"] = 1

        form = ProjectCreateForm(data=dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertTrue(is_valid)
        companies = Company.objects.all()
        self.assertEqual(1, companies.count())
        self.assertEqual(operator, companies.first().contact)


class ProjectUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.contract1, cls.contract2, cls.contract3 = create_project()

    def __get_dict_for_post(self):
        return {
            "company_name": "Aperture Science",
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
            "contract3_counter_name": "Corrective",
        }

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = ProjectUpdateForm(company=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "company_name": [expected],
                "contract1_counter_name": [expected],
                "contract2_counter_name": [expected],
                "contract3_counter_name": [expected],
                "contract1_date": [expected],
                "contract2_date": [expected],
                "contract3_date": [expected],
                "contract1_visible": [expected],
                "contract2_visible": [expected],
                "contract3_visible": [expected],
                "contract1_total_type": [expected],
                "contract2_total_type": [expected],
                "contract3_total_type": [expected],
                "contract1_number_hours": [expected],
                "contract2_number_hours": [expected],
                "contract3_number_hours": [expected],
            },
        )

    def test_valid_form_update_a_company(self):
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())

    def test_valid_form_update_a_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_update_contract_counter_name(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_counter_name"] = "Experiment"
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, counter_name="Experiment").count())

    def test_valid_form_update_contract_start_date(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_date"] = datetime.date(2012, 12, 21)
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, start=datetime.date(2012, 12, 21)).count()
        )

    def test_valid_form_update_contract_total_type(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 1
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = self.contract1.number_hours
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_update_a_company_and_invisible_available_time_contract(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_visible"] = 0
        dict_for_post["contract1_total_type"] = AVAILABLE_TOTAL_TIME
        dict_for_post["contract1_number_hours"] = 80
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1,
            MaintenanceContract.objects.filter(
                company_id=company,
                maintenance_type_id=1,
                visible=False,
                total_type=AVAILABLE_TOTAL_TIME,
                number_hours=80,
                disabled=False,
            ).count(),
        )

    def test_invalid_form_update_already_existing_company(self):
        CompanyFactory.create(name="Aperture Science")
        dict_for_post = self.__get_dict_for_post()
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors["company_name"].as_text(), "* " + str(_("This company already exists.")))

    def test_when_i_bound_a_update_form_with_under_min_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = -10
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 0}
        self.assertEqual(form.errors["contract1_number_hours"].as_text(), "* %s" % expected)

    def test_when_i_bound_a_update_form_with_string_as_number_hours_i_have_an_error(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contract1_number_hours"] = "I'm a duration"
        form = ProjectUpdateForm(company=self.company, data=dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["contract1_number_hours"], [expected])

    def test_when_i_send_a_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contact"] = operator.pk

        form = ProjectUpdateForm(company=self.company, data=dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(operator, company.contact)

    def test_when_i_remove_the_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        self.company.operator = operator
        self.company.save()
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contact"] = None

        form = ProjectUpdateForm(company=self.company, data=dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(None, company.contact)

    def test_when_i_keep_the_same_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        self.company.operator = operator
        self.company.save()
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["contact"] = operator.pk

        form = ProjectUpdateForm(company=self.company, data=dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(operator, company.contact)
