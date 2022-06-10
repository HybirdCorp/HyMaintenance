import datetime
import os

from customers.models import Company
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from freezegun import freeze_time
from freezegun.api import FakeDate
from maintenance.forms.project import INACTIF_CONTRACT_INPUT
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import MaintenanceCreditFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project
from toolkit.tests import create_temporary_image

from django.core.files import File
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ...views.project import ProjectCreateView
from ...views.project import ProjectCustomizeView
from ...views.project import ProjectDetailsView
from ...views.project import ProjectListArchiveView
from ...views.project import ProjectListUnarchiveView
from ...views.project import ProjectUpdateView


class ProjectCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:create_project")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = ProjectCreateView()
        view.request = request
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual(3, len(context["maintenance_types"]))
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_no_email_alert_field_on_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertNotContains(response, 'class="form-row row-email-alert')
        self.assertNotContains(response, 'class="form-row row-credit-min')
        self.assertNotContains(response, 'class="form-row row-recipient')

    def test_admin_can_post_form_to_create_a_project(self):
        operator = OperatorUserFactory(first_name="Chell")
        company_name = "Black Mesa"
        displayed_month_number = 6
        # No support contract
        contract0_visible = INACTIF_CONTRACT_INPUT
        contract0_total_type = 0
        contract0_credited_hours = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract1_visible = 0  # FALSE
        contract1_total_type = AVAILABLE_TOTAL_TIME
        contract1_credited_hours = 80

        # correction contract, visible for manager, consummed total time
        contract2_visible = 1  # TRUE
        contract2_total_type = CONSUMMED_TOTAL_TIME
        contract2_credited_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url,
            {
                "company_name": company_name,
                "displayed_month_number": displayed_month_number,
                "contact": operator.pk,
                "contract0_visible": contract0_visible,
                "contract0_total_type": contract0_total_type,
                "contract0_credited_hours": contract0_credited_hours,
                "contract0_counter_name": "Maintenance",
                "contract0_date": datetime.date.today(),
                "contract1_visible": contract1_visible,
                "contract1_total_type": contract1_total_type,
                "contract1_credited_hours": contract1_credited_hours,
                "contract1_counter_name": "Support",
                "contract1_date": datetime.date.today(),
                "contract2_visible": contract2_visible,
                "contract2_total_type": contract2_total_type,
                "contract2_credited_hours": contract2_credited_hours,
                "contract2_counter_name": "Corrective",
                "contract2_date": datetime.date.today(),
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))

        self.assertEqual(1, Company.objects.filter(name=company_name).count())
        company = Company.objects.get(name=company_name)
        contracts = MaintenanceContract.objects.filter(company_id=company.id)
        self.assertEqual(3, contracts.count())


class ProjectUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, _, _, _ = create_project(contract1={"credit_counter": True})

        cls.form_url = reverse("high_ui:update_project", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = ProjectUpdateView()
        view.request = request
        view.user = self.user
        view.company = self.company

        context = view.get_context_data()
        self.assertEqual(3, len(context["maintenance_types"]))
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_email_alert_field_on_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(response, 'class="form-row row-email-alert')
        self.assertContains(response, 'class="form-row row-credit-min')
        self.assertContains(response, 'class="form-row row-recipient')

    def test_i_can_post_and_form_to_update_a_project(self):
        operator = OperatorUserFactory(first_name="Chell")
        operator.operator_for.add(self.company)
        company_name = "Aperture Science"
        displayed_month_number = 6
        # No support contract
        contract0_visible = INACTIF_CONTRACT_INPUT
        contract0_total_type = CONSUMMED_TOTAL_TIME
        contract0_email_alert = False
        contract0_credited_hours_min = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract1_visible = 0  # FALSE
        contract1_total_type = AVAILABLE_TOTAL_TIME
        contract1_email_alert = True
        contract1_credited_hours_min = 20

        # correction contract, visible for manager, consummed total time
        contract2_visible = 1  # TRUE
        contract2_total_type = CONSUMMED_TOTAL_TIME
        contract2_email_alert = False
        contract2_credited_hours_min = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url,
            {
                "company_name": company_name,
                "displayed_month_number": displayed_month_number,
                "contact": operator.pk,
                "contract0_visible": contract0_visible,
                "contract0_total_type": contract0_total_type,
                "contract0_counter_name": "Maintenance",
                "contract0_date": datetime.date.today(),
                "contract0_email_alert": contract0_email_alert,
                "contract0_credited_hours_min": contract0_credited_hours_min,
                "contract1_visible": contract1_visible,
                "contract1_total_type": contract1_total_type,
                "contract1_counter_name": "Support",
                "contract1_date": datetime.date.today(),
                "contract1_email_alert": contract1_email_alert,
                "contract1_credited_hours_min": contract1_credited_hours_min,
                "contract2_visible": contract2_visible,
                "contract2_total_type": contract2_total_type,
                "contract2_counter_name": "Corrective",
                "contract2_date": datetime.date.today(),
                "contract2_email_alert": contract2_email_alert,
                "contract2_credited_hours_min": contract2_credited_hours_min,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertTrue(Company.objects.get(name=company_name, pk=self.company.pk))
        contracts = MaintenanceContract.objects.filter(company_id=self.company.id)
        self.assertEqual(3, contracts.count())


class ProjectDetailsViewTestCase(TestCase):
    def setUp(self):
        self.company, self.contract1, self.contract2, self.contract3 = create_project(
            contract1={"credit_counter": True}
        )
        self.form_url = reverse("high_ui:project_details", args=[self.company.slug_name])
        self.login_url = reverse("login") + "?next=" + self.form_url

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_can_seen_his_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_can_seen_his_company(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_seen_his_archived_company(self):
        company, _, _, _ = create_project(company={"is_archived": True})
        view_url = reverse("high_ui:project_details", args=[company.slug_name])
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(view_url)

        self.assertEqual(response.status_code, 404)

    def test_operator_cannot_seen_other_company(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_seen_a_company(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_seen_an_archived_company(self):
        company, _, _, _ = create_project(company={"is_archived": True})
        view_url = reverse("high_ui:project_details", args=[company.slug_name])
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(view_url)

        self.assertEqual(response.status_code, 404)

    def test_display_extra_credit(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        MaintenanceCreditFactory(contract=self.contract1, company=self.company, hours_number=10, date=now().date())

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="history-item-duration duration">+10h</td>')

    def test_display_extra_credit_optional_subject(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.contract1.total_type = AVAILABLE_TOTAL_TIME
        self.contract1.save()
        subject = "The cake is lie"
        MaintenanceCreditFactory(
            contract=self.contract1, company=self.company, hours_number=10, date=now().date(), subject=subject
        )

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, subject)

    def test_staff_company_display_project_header(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.client.login(username=admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<span class="dashboard-title">Black Mesa</span>')
        self.assertContains(response, '<span class="dashboard-title">company</span>')

    def test_manager_company_display_project_header(self):
        user = ManagerUserFactory(email="glados@aperture-science.com", password="azerty", company=self.company)
        self.client.login(username=user.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="dashboard-title">Black Mesa</span>')
        self.assertNotContains(response, '<span class="dashboard-title">company</span>')

    def test_admin_add_credit_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.contract1.total_type = AVAILABLE_TOTAL_TIME
        self.contract1.save()

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Add hours"))

    def test_manager_buy_credit_button(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)
        self.contract1.total_type = AVAILABLE_TOTAL_TIME
        self.contract1.save()

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Buy hours"))

    def test_admin_no_add_credit_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.contract1.total_type = CONSUMMED_TOTAL_TIME
        self.contract1.save()
        self.contract2.total_type = CONSUMMED_TOTAL_TIME
        self.contract2.save()
        self.contract3.total_type = CONSUMMED_TOTAL_TIME
        self.contract3.save()

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Add hours"))

    def test_no_email_alert_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.contract1.total_type = CONSUMMED_TOTAL_TIME
        self.contract1.save()
        self.contract2.disabled = True
        self.contract2.total_type = AVAILABLE_TOTAL_TIME
        self.contract2.save()
        self.contract3.disabled = True
        self.contract3.save()

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Email alert"))

    def test_email_alert_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.contract1.disabled = False
        self.contract1.total_type = AVAILABLE_TOTAL_TIME
        self.contract1.save()

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Email alerts"))

    def test_manager_has_no_add_issue_button(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Register an issue"))

    def test_operator_has_add_issue_button(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Register an issue"))

    def test_admin_has_add_issue_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Register an issue"))

    def test_manager_has_no_add_recurrence_button(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Manage recurrence"))

    def test_operator_has_add_recurrence_button(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Manage recurrence"))

    def test_admin_has_add_recurrence_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Manage recurrence"))


class MonthDisplayInFrenchTestCase(TestCase):
    def test_month_display_in_french(self):
        company, _, _, _ = create_project()
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(reverse("high_ui:project_details", args=[company.slug_name]))

        month = now().date().month
        french_months = [
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ]

        self.assertContains(response, french_months[month - 1])


@freeze_time("2020, 2, 29")
class GetContextDataProjectDetailsSpecificTestCase(TestCase):
    def empty_month_info_assertion(self, contract, company, history):
        expected_info = {
            'contracts': {
                str(contract.id): {
                    'consumed': 0,
                    'counter_name': 'Maintenance',
                    'credited': 0,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
            },
            'events': [],
            'events_count': 0
        }

        self.assertEqual(company.displayed_month_number, len(history))

        for month, month_info in history.items():
            self.assertEqual(month_info, expected_info)

    def test_initialize_history_data_structure(self):
        company, contract, _, _ = create_project(
            contract1={"disabled": True},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        last_month, history = view.initialize_history_data_structure(contracts)

        expected_last_month = datetime.date(2019, 9, 1)
        expected_months = [
            expected_last_month,
            datetime.date(2019, 10, 1),
            datetime.date(2019, 11, 1),
            datetime.date(2019, 12, 1),
            datetime.date(2020, 1, 1),
            datetime.date(2020, 2, 1)
        ]
        expected_info = {
            'contracts': {},
            'events': [],
            'events_count': 0
        }

        self.assertEqual(expected_last_month, last_month)
        self.assertEqual(len(expected_months), len(history))

        for expected_month in expected_months:
            self.assertIn(expected_month, history)

        for expected_month in expected_months:
            self.assertEqual(history[expected_month], expected_info)

    def test_history_no_contract(self):
        company, contract, _, _ = create_project(
            contract1={"disabled": True},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        expected_info = {
            'contracts': {},
            'events': [],
            'events_count': 0
        }

        self.assertEqual(company.displayed_month_number, len(history))

        for month, month_info in history.items():
            self.assertEqual(month_info, expected_info)
            self.assertEqual(month_info, expected_info)

    def test_history_available_contract__no_event(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        self.empty_month_info_assertion(contract, company, history)

    def test_history_available_contract__one_passed_issue(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2020, 2, 29)
        event_month = datetime.date(2020, 2, 1)
        passed_issue = MaintenanceIssueFactory(
            company=company, contract=contract, number_minutes=12, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        expected_info = {
            'contracts': {
                str(contract.id): {
                    'consumed': 12,
                    'counter_name': 'Maintenance',
                    'credited': 0,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
            },
            'events': [{
                'company__slug_name': 'black-mesa',
                'company_issue_number': passed_issue.company_issue_number,
                'contract': passed_issue.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2020, 2, 29),
                'number_minutes': 12,
                'subject': "It's "
                           'not '
                           'working',
                'type': 'issue'
            }],
            'events_count': 1
        }

        self.assertEqual(company.displayed_month_number, len(history))

        self.assertEqual(history[event_month], expected_info)

    def test_history_available_contract__one_passed_credit(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2020, 2, 29)
        event_month = datetime.date(2020, 2, 1)
        passed_credit = MaintenanceCreditFactory(
            company=company, contract=contract, hours_number=10, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        expected_info = {
            'contracts': {
                str(contract.id): {
                    'consumed': 0,
                    'counter_name': 'Maintenance',
                    'credited': 10,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
            },
            'events': [{
                'company__slug_name': 'black-mesa',
                'contract': passed_credit.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2020, 2, 29),
                'hours_number': 10,
                'id': passed_credit.id,
                'subject': None,
                'type': 'credit',
                'is_available_time_counter': True,
            }],
            'events_count': 1
        }

        self.assertEqual(company.displayed_month_number, len(history))

        self.assertEqual(history[event_month], expected_info)

    def test_history_available_contract__one_future_issue(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2023, 2, 28)
        MaintenanceIssueFactory(
            company=company, contract=contract, number_minutes=12, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        self.empty_month_info_assertion(contract, company, history)

    def test_history_available_contract__one_future_credit(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2023, 2, 28)
        MaintenanceCreditFactory(
            company=company, contract=contract, hours_number=10, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        history = view.get_history(contracts)

        self.empty_month_info_assertion(contract, company, history)

    def test_forecast_no_contract(self):
        company, contract, _, _ = create_project(
            contract1={"disabled": True},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        self.assertEqual(0, len(forecast))

    def test_forecast_available_contract__no_event(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        self.assertEqual(0, len(forecast))

    def test_forecast_available_contract__one_passed_issue(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2020, 2, 29)
        MaintenanceIssueFactory(
            company=company, contract=contract, number_minutes=12, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        self.assertEqual(0, len(forecast))

    def test_forecast_available_contract__one_passed_credit(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2020, 2, 29)
        MaintenanceCreditFactory(
            company=company, contract=contract, hours_number=10, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        self.assertEqual(0, len(forecast))

    def test_forecast_available_contract__one_future_issue(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2023, 2, 28)
        event_month = datetime.date(2023, 2, 1)
        future_issue = MaintenanceIssueFactory(
            company=company, contract=contract, number_minutes=12, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        expected_info = {
            'contracts': {
                str(contract.id): {
                    'consumed': 12,
                    'counter_name': 'Maintenance',
                    'credited': 0,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
            },
            'events': [{
                'company__slug_name': 'black-mesa',
                'company_issue_number': future_issue.company_issue_number,
                'contract': future_issue.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2023, 2, 28),
                'number_minutes': 12,
                'subject': "It's "
                           'not '
                           'working',
                'type': 'issue'
            }],
            'events_count': 1
        }

        self.assertEqual(1, len(forecast))

        self.assertEqual(forecast[event_month], expected_info)

    def test_forecast_available_contract__one_future_credit(self):
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": datetime.date(2019, 1, 1)},
            contract2={"disabled": True},
            contract3={"disabled": True}
        )
        event_date = datetime.date(2023, 2, 28)
        event_month = datetime.date(2023, 2, 1)
        future_credit = MaintenanceCreditFactory(
            company=company, contract=contract, hours_number=10, date=event_date
        )
        contracts = MaintenanceContract.objects.filter_enabled(company=company)

        view = ProjectDetailsView()
        view.company = company

        forecast = view.get_forecast(contracts)

        expected_info = {
            'contracts': {
                str(contract.id): {
                    'consumed': 0,
                    'counter_name': 'Maintenance',
                    'credited': 10,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
            },
            'events': [{
                'company__slug_name': 'black-mesa',
                'contract': future_credit.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2023, 2, 28),
                'hours_number': 10,
                'id': future_credit.id,
                'subject': None,
                'type': 'credit',
                'is_available_time_counter': True,
            }],
            'events_count': 1
        }

        self.assertEqual(1, len(forecast))

        self.assertEqual(forecast[event_month], expected_info)


@freeze_time("2020, 2, 29")
class GetContextDataProjectDetailsGeneralTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, cls.avail_contract, cls.disabled_contract, cls.consu_contract = create_project(
            contract1={"start": datetime.date(2020, 2, 29), "credit_counter": True},
            contract2={"disabled": True},
            contract3={"visible": False, "counter_name": "Custom"}
        )
        cls.creation_credit = MaintenanceCredit.objects.filter(contract=cls.avail_contract).first()
        cls.passed_issue1 = MaintenanceIssueFactory(
            company=cls.company, contract=cls.avail_contract, number_minutes=12, date=datetime.date(2020, 2, 29)
        )
        MaintenanceIssueFactory(
            company=cls.company, contract=cls.avail_contract, number_minutes=12, date=datetime.date(2018, 2, 28)
        )
        MaintenanceIssueFactory(
            company=cls.company, contract=cls.disabled_contract, number_minutes=12, date=datetime.date(2020, 2, 29)
        )
        cls.passed_issue2 = MaintenanceIssueFactory(
            company=cls.company, contract=cls.consu_contract, number_minutes=12, date=datetime.date(2020, 2, 29)
        )
        cls.future_issue = MaintenanceIssueFactory(
            company=cls.company, contract=cls.consu_contract, number_minutes=42, date=datetime.date(2022, 2, 20)
        )
        cls.future_credit = MaintenanceCreditFactory(
            company=cls.company, contract=cls.avail_contract, hours_number=10, date=datetime.date(2022, 2, 20)
        )
        cls.contracts = MaintenanceContract.objects.filter(company=cls.company, disabled=False)

    def test_get_history(self):
        view = ProjectDetailsView()
        view.company = self.company

        history = view.get_history(self.contracts)

        expected_empty_months = [
            datetime.date(2019, 9, 1),
            datetime.date(2019, 10, 1),
            datetime.date(2019, 11, 1),
            datetime.date(2019, 12, 1),
            datetime.date(2020, 1, 1),
        ]
        not_empty_month = datetime.date(2020, 2, 1)
        expected_months = expected_empty_months + [not_empty_month, ]
        expected_empty_info = {
            'contracts': {
                str(self.avail_contract.id): {
                    'consumed': 0,
                    'counter_name': 'Maintenance',
                    'credited': 0,
                    'css_class': 'type-maintenance',
                    'is_available_time_counter': True,
                },
                str(self.consu_contract.id): {
                    'consumed': 0,
                    'counter_name': 'Custom',
                    'credited': 0,
                    'css_class': 'type-correction',
                    'is_available_time_counter': False,
                },
            },
            'events': [],
            'events_count': 0
        }

        expected_not_empty_contracts_info = {
            str(self.avail_contract.id): {
                'consumed': 12,
                'counter_name': 'Maintenance',
                'credited': 20,
                'css_class': 'type-maintenance',
                'is_available_time_counter': True,
            },
            str(self.consu_contract.id): {
                'consumed': 12,
                'counter_name': 'Custom',
                'credited': 0,
                'css_class': 'type-correction',
                'is_available_time_counter': False,
            },
        }

        expected_not_empty_events_info = [
            {
                'company__slug_name': 'black-mesa',
                'company_issue_number': self.passed_issue1.company_issue_number,
                'contract': self.passed_issue1.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2020, 2, 29),
                'number_minutes': 12,
                'subject': "It's "
                           'not '
                           'working',
                'type': 'issue'
            }, {
                'company__slug_name': 'black-mesa',
                'company_issue_number': self.passed_issue2.company_issue_number,
                'contract': self.passed_issue2.contract.id,
                'counter_name': 'Custom',
                'css_class': 'type-correction',
                'date': FakeDate(2020, 2, 29),
                'number_minutes': 12,
                'subject': "It's "
                           'not '
                           'working',
                'type': 'issue'
            }, {
                'company__slug_name': 'black-mesa',
                'contract': self.creation_credit.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2020, 2, 29),
                'hours_number': 20,
                'id': self.creation_credit.id,
                'subject': None,
                'type': 'credit',
                'is_available_time_counter': True,
            }]

        self.assertEqual(len(expected_months), len(history))

        for expected_month in expected_months:
            self.assertIn(expected_month, history)

        for expected_empty_month in expected_empty_months:
            self.assertEqual(history[expected_empty_month], expected_empty_info)

        for key in ("contracts", "events_count", "events"):
            self.assertIn(key, history[not_empty_month])

        self.assertEqual(history[not_empty_month]['events_count'], 3)
        self.assertEqual(history[not_empty_month]['contracts'], expected_not_empty_contracts_info)

        self.assertEqual(history[not_empty_month]['events'], expected_not_empty_events_info)

    def test_get_forecast(self):
        self.maxDiff = None
        view = ProjectDetailsView()
        view.company = self.company

        forecast = view.get_forecast(self.contracts)

        expected_month = datetime.date(2022, 2, 1)

        expected_contracts_info = {
            str(self.avail_contract.id): {
                'consumed': 0,
                'counter_name': 'Maintenance',
                'credited': 10,
                'css_class': 'type-maintenance',
                'is_available_time_counter': True,
            },
            str(self.consu_contract.id): {
                'consumed': 42,
                'counter_name': 'Custom',
                'credited': 0,
                'css_class': 'type-correction',
                'is_available_time_counter': False,
            },
        }

        expected_events_info = [
            {
                'company__slug_name': 'black-mesa',
                'company_issue_number': self.future_issue.company_issue_number,
                'contract': self.future_issue.contract.id,
                'counter_name': 'Custom',
                'css_class': 'type-correction',
                'date': FakeDate(2022, 2, 20),
                'number_minutes': 42,
                'subject': "It's "
                           'not '
                           'working',
                'type': 'issue'
            }, {
                'company__slug_name': 'black-mesa',
                'contract': self.future_credit.contract.id,
                'counter_name': 'Maintenance',
                'css_class': 'type-maintenance',
                'date': FakeDate(2022, 2, 20),
                'hours_number': 10,
                'id': self.future_credit.id,
                'subject': None,
                'type': 'credit',
                'is_available_time_counter': True,
            }]

        self.assertEqual(1, len(forecast))

        self.assertIn(expected_month, forecast)

        for key in ("contracts", "events_count", "events"):
            self.assertIn(key, forecast[expected_month])

        self.assertEqual(forecast[expected_month]['events_count'], 2)
        self.assertEqual(forecast[expected_month]['contracts'], expected_contracts_info)

        self.assertEqual(forecast[expected_month]['events'], expected_events_info)

    def test_get_context_data(self):
        form_url = reverse("high_ui:project_details", args=[self.company.slug_name])
        factory = RequestFactory()
        request = factory.get(form_url)

        user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        request.user = user
        view = ProjectDetailsView()
        view.request = request
        view.user = user
        view.object = self.company
        view.company = self.company

        context = view.get_context_data()
        self.assertIn("forecast", context.keys())
        self.assertEqual(1, len(context["forecast"]))
        self.assertIn("history", context.keys())
        self.assertEqual(6, len(context["history"]))


class ProjectListArchiveViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:archive_projects")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def setUp(self):
        self.avail_contract = CompanyFactory(name="Black Mesa", is_archived=True)
        self.c2 = CompanyFactory(name="Aperture Science")

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ProjectListArchiveView()
        view.request = request
        view.user = self.admin

        context = view.get_context_data()
        self.assertIn("projects_number", context.keys())
        self.assertEqual(1, context["projects_number"])
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_project_archive_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"projects": self.c2.pk}, follow=True)

        self.assertRedirects(response, reverse("high_ui:admin"))
        companies = Company.objects.filter(is_archived=True)
        self.assertEqual(2, companies.count())
        self.assertIn(self.c2, companies)


class ProjectListUnunarchiveViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:unarchive_projects")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def setUp(self):
        self.avail_contract = CompanyFactory(name="Black Mesa", is_archived=True)
        self.c2 = CompanyFactory(name="Aperture Science")

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ProjectListUnarchiveView()
        view.request = request
        view.user = self.admin

        context = view.get_context_data()
        self.assertIn("projects_number", context.keys())
        self.assertEqual(1, context["projects_number"])
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_project_unarchive_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"projects": self.avail_contract.pk}, follow=True)

        self.assertRedirects(response, reverse("high_ui:admin"))
        companies = Company.objects.filter(is_archived=False)
        self.assertEqual(2, companies.count())
        self.assertIn(self.avail_contract, companies)


class ProjectCustomizeViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, _, _, _ = create_project()

        cls.form_url = reverse("high_ui:customize_project", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = ProjectCustomizeView()
        view.company = self.company
        view.object = self.company
        view.request = request
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_update_a_project(self):
        operator = OperatorUserFactory(first_name="Chell")
        operator.operator_for.add(self.company)
        company_name = "Aperture Science"
        color = "#000"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url,
            {"name": company_name, "contact": operator.pk, "has_custom_color": True, "color": color},
            follow=True,
        )

        company = Company.objects.get(pk=self.company.pk)
        self.assertRedirects(response, reverse("high_ui:project_details", kwargs={"company_name": company.slug_name}))
        self.assertEquals(company_name, company.name)
        self.assertEquals(color, company.color)
        self.assertEquals(operator, company.contact)


class ProjectHeaderTestCase(TestCase):
    def setUp(self):
        self.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.company, self.contract, _, _ = create_project()
        self.view_url = reverse("high_ui:project_details", args=[self.company.slug_name])
        self.login_url = reverse("login") + "?next=" + self.view_url

    def test_default_display(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="dashboard type-maintenance" >')
        self.assertNotContains(response, '<div class="dashboard-logo">')

    def test_dark_font_and_custom_color_and_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = True
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard dark" style="background:#000;">')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_light_font_and_custom_color_and_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = False
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard light" style="background:#000;">')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_default_color_with_logo_display(self):
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard type-maintenance" >')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_light_font_and_custom_color_without_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = False
        self.company.save()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="dashboard light" style="background:#000;">')
        self.assertNotContains(response, '<div class="dashboard-logo">')
