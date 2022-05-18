import datetime

from customers.models import Company
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.forms.project import INACTIF_CONTRACT_INPUT
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceCredit
from maintenance.models import MaintenanceType
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ..factories import create_project


class ProjectCreateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.maintenance_types = MaintenanceType.objects.order_by("id")

    def setUp(self):
        self.dict_for_post = {
            "company_name": "Black Mesa",
            "displayed_month_number": 6,
        }
        for index, maintenance_type in enumerate(self.maintenance_types):
            self.dict_for_post.update({
                f"contract{index}_visible": INACTIF_CONTRACT_INPUT,
                f"contract{index}_total_type": 0,
                f"contract{index}_credited_hours": 0,
                f"contract{index}_date": datetime.date.today(),
                f"contract{index}_counter_name": maintenance_type.name,
            })

    def test_create_form_maintenance_type_initial_values(self):
        form = ProjectCreateForm(initial={"test": "initial not empty"})

        for index, maintenance_type in enumerate(self.maintenance_types):
            field_name = f"contract{index}_counter_name"
            self.assertEqual(
                maintenance_type.name,
                form.get_initial_for_field(form.fields[field_name], field_name),
            )

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = ProjectCreateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        expected_dict_errors = {
            "company_name": [expected],
            "displayed_month_number": [expected],
        }
        for index, maintenance_type in enumerate(self.maintenance_types):
            expected_dict_errors.update({
                f"contract{index}_counter_name": [expected],
                f"contract{index}_date": [expected],
                f"contract{index}_visible": [expected],
                f"contract{index}_total_type": [expected],
                f"contract{index}_credited_hours": [expected],
            })
        self.assertDictEqual(form.errors, expected_dict_errors)

    def test_form_not_valid_when_no_contract(self):

        form = ProjectCreateForm(data=self.dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertFalse(is_valid)
        self.assertDictEqual(form.errors, {"__all__": [_("You have to create at least one contract on the project.")]})

    def test_valid_form_create_a_consummed_time_support_contract(self):
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract0_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=self.dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_create_a_available_time_support_contract(self):
        credited_hours = 100
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract0_total_type"] = AVAILABLE_TOTAL_TIME
        self.dict_for_post["contract0_credited_hours"] = credited_hours
        form = ProjectCreateForm(data=self.dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        contracts = MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False)
        self.assertEqual(1, contracts.count())
        self.assertEqual(
            1,
            MaintenanceCredit.objects.filter(
                company_id=company, contract=contracts.first(), hours_number=credited_hours
            ).count(),
        )

    def test_valid_form_create_a_maintenance_contract(self):
        self.dict_for_post["contract1_visible"] = 1
        self.dict_for_post["contract1_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=self.dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=2, disabled=False).count()
        )

    def test_valid_form_create_contracts_counter_name(self):
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract1_visible"] = 1
        self.dict_for_post["contract2_visible"] = 1
        self.dict_for_post["contract0_counter_name"] = "Reduice"
        self.dict_for_post["contract1_counter_name"] = "Reuse"
        self.dict_for_post["contract2_counter_name"] = "Recycle"
        form = ProjectCreateForm(data=self.dict_for_post)

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
        form = ProjectCreateForm(data=self.dict_for_post)

        form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")
        self.assertEqual(2, company.managed_by.all().count())

    def test_valid_form_create_a_correction_contract(self):
        self.dict_for_post["contract2_visible"] = 1
        self.dict_for_post["contract2_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectCreateForm(data=self.dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=3, disabled=False).count()
        )

    def test_valid_form_create_a_company_and_invisible_available_time_contract(self):
        self.dict_for_post["contract0_visible"] = 0
        self.dict_for_post["contract0_total_type"] = AVAILABLE_TOTAL_TIME
        self.dict_for_post["contract0_credited_hours"] = 80
        form = ProjectCreateForm(data=self.dict_for_post)

        is_valid = form.is_valid()
        form.create_company_and_contracts()
        company = Company.objects.get(name="Black Mesa")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        contracts = MaintenanceContract.objects.filter(
            company_id=company, maintenance_type_id=1, visible=False, total_type=AVAILABLE_TOTAL_TIME, disabled=False
        )
        self.assertEqual(1, contracts.count())
        credits = MaintenanceCredit.objects.filter(contract=contracts.first(), company=company, hours_number=80)
        self.assertEqual(1, credits.count())

    def test_invalid_form_create_already_existing_company(self):
        CompanyFactory.create(name="Black Mesa")
        form = ProjectCreateForm(data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors["company_name"].as_text(), "* " + str(_("This company already exists.")))

    def test_when_i_bound_a_create_form_with_under_min_credited_hours_i_have_an_error(self):
        self.dict_for_post["contract0_credited_hours"] = -10
        form = ProjectCreateForm(data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 0}
        self.assertEqual(form.errors["contract0_credited_hours"].as_text(), "* %s" % expected)

    def test_when_i_bound_a_create_form_with_string_as_credited_hours_i_have_an_error(self):
        self.dict_for_post["contract1_credited_hours"] = "I'm a duration"
        form = ProjectCreateForm(data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["contract1_credited_hours"], [expected])

    def test_when_i_send_a_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        self.dict_for_post["contact"] = operator.pk
        self.dict_for_post["contract0_visible"] = 1

        form = ProjectCreateForm(data=self.dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertTrue(is_valid)
        companies = Company.objects.all()
        self.assertEqual(1, companies.count())
        self.assertEqual(operator, companies.first().contact)

    def test_create_project_when_there_are_archived_operators(self):
        operator = OperatorUserFactory(first_name="Chell", is_active=True)
        operator2 = OperatorUserFactory(first_name="NotChell", is_active=False)
        self.dict_for_post["contract0_visible"] = 1

        form = ProjectCreateForm(data=self.dict_for_post)
        is_valid = form.is_valid()
        form.create_company_and_contracts()

        self.assertTrue(is_valid)
        companies = Company.objects.all()
        self.assertEqual(1, companies.count())
        operators = companies.first().managed_by.all()
        self.assertIn(operator, operators)
        self.assertNotIn(operator2, operators)


class ProjectUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.maintenance_types = MaintenanceType.objects.order_by("id")

    def setUp(self):
        self.company, self.contract0, self.contract1, self.contract2 = create_project()

        self.dict_for_post = {
            "company_name": "Aperture Science",
            "displayed_month_number": 6,
        }
        for index, maintenance_type in enumerate(self.maintenance_types):
            self.dict_for_post.update({
                f"contract{index}_visible": INACTIF_CONTRACT_INPUT,
                f"contract{index}_total_type": 0,
                f"contract{index}_credited_hours": 0,
                f"contract{index}_date": datetime.date.today(),
                f"contract{index}_counter_name": maintenance_type.name,
                f"contract{index}_email_alert": False,
                f"contract{index}_credited_hours_min": 0,
            })

    def test_contact_queryset(self):
        operator = OperatorUserFactory(first_name="Chell")
        operator.operator_for.add(self.company)
        form = ProjectUpdateForm(company=self.company, data={})
        self.assertEqual([operator], list(form.fields["contact"]._queryset))

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = ProjectUpdateForm(company=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "company_name": [expected],
                "displayed_month_number": [expected],
                "contract0_counter_name": [expected],
                "contract1_counter_name": [expected],
                "contract2_counter_name": [expected],
                "contract0_date": [expected],
                "contract1_date": [expected],
                "contract2_date": [expected],
                "contract0_visible": [expected],
                "contract1_visible": [expected],
                "contract2_visible": [expected],
                "contract0_total_type": [expected],
                "contract1_total_type": [expected],
                "contract2_total_type": [expected],
            },
        )

    def test_valid_form_update_a_company(self):
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())

    def test_valid_form_update_a_contract(self):
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract0_total_type"] = CONSUMMED_TOTAL_TIME
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Aperture Science")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_update_contract_counter_name(self):
        self.dict_for_post["contract0_counter_name"] = "Experiment"
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Aperture Science")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(company_id=company, counter_name="Experiment").count())

    def test_valid_form_update_displayed_month_number(self):
        self.dict_for_post["displayed_month_number"] = 12
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)

        self.company.refresh_from_db()
        self.assertEqual(12, self.company.displayed_month_number)

    def test_valid_form_update_contract_start_date(self):
        self.dict_for_post["contract0_date"] = datetime.date(2012, 12, 21)
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Aperture Science")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, start=datetime.date(2012, 12, 21)).count()
        )

    def test_valid_form_update_contract_total_type(self):
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract0_total_type"] = AVAILABLE_TOTAL_TIME
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Aperture Science")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1, MaintenanceContract.objects.filter(company_id=company, maintenance_type_id=1, disabled=False).count()
        )

    def test_valid_form_update_a_company_and_invisible_available_time_contract(self):
        self.dict_for_post["contract0_visible"] = 0
        self.dict_for_post["contract0_total_type"] = AVAILABLE_TOTAL_TIME
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()
        company = Company.objects.get(name="Aperture Science")

        self.assertTrue(is_valid)
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(
            1,
            MaintenanceContract.objects.filter(
                company_id=company,
                maintenance_type_id=1,
                visible=False,
                total_type=AVAILABLE_TOTAL_TIME,
                disabled=False,
            ).count(),
        )

    def test_invalid_form_update_already_existing_company(self):
        CompanyFactory.create(name="Aperture Science")
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors["company_name"].as_text(), "* " + str(_("This company already exists.")))

    def test_when_i_bound_a_update_form_with_under_min_credited_hours_i_have_an_error(self):
        self.dict_for_post["contract0_credited_hours_min"] = -10
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 0}
        self.assertEqual(form.errors["contract0_credited_hours_min"].as_text(), "* %s" % expected)

    def test_when_i_bound_a_update_form_with_string_as_credited_hours_min_i_have_an_error(self):
        self.dict_for_post["contract0_credited_hours_min"] = "I'm a duration"
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["contract0_credited_hours_min"], [expected])

    def test_when_i_send_a_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        operator.operator_for.add(self.company)
        self.dict_for_post["contact"] = operator.pk

        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(operator, company.contact)

    def test_when_i_remove_the_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        self.company.operator = operator
        self.company.save()
        self.dict_for_post["contact"] = None

        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(None, company.contact)

    def test_when_i_keep_the_same_contact(self):
        operator = OperatorUserFactory(first_name="Chell")
        operator.operator_for.add(self.company)
        self.dict_for_post["contact"] = operator.pk

        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)
        is_valid = form.is_valid()
        form.update_company_and_contracts()

        self.assertTrue(is_valid)
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(operator, company.contact)

    def test_when_i_add_email_alert(self):
        manager = ManagerUserFactory(company=self.company)
        self.dict_for_post["contract0_visible"] = 1
        self.dict_for_post["contract0_total_type"] = AVAILABLE_TOTAL_TIME
        self.dict_for_post["contract0_email_alert"] = True
        self.dict_for_post["contract0_credited_hours_min"] = 40
        self.dict_for_post["contract0_recipient"] = manager.pk
        form = ProjectUpdateForm(company=self.company, data=self.dict_for_post)

        is_valid = form.is_valid()
        form.update_company_and_contracts()

        contract = MaintenanceContract.objects.get(pk=self.contract0.pk)
        self.assertTrue(is_valid)
        self.assertTrue(contract.email_alert)
        self.assertEqual(40, contract.credited_hours_min)
        self.assertEqual(manager, contract.recipient)
