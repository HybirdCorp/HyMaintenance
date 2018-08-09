import datetime

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.models import Company
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.forms.project import INACTIF_CONTRACT_INPUT
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import MaintenanceCreditFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from ...views.project import ProjectCreateView
from ...views.project import ProjectDetailsView
from ...views.project import ProjectUpdateView


class ProjectCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:create_project")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data_maintenance_types(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = ProjectCreateView()
        view.request = request
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual(3, len(context["maintenance_types"]))

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_create_a_project(self):
        operator = OperatorUserFactory(first_name="Chell")
        company_name = "Black Mesa"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url,
            {
                "company_name": company_name,
                "contact": operator.pk,
                "contract1_visible": contract1_visible,
                "contract1_total_type": contract1_total_type,
                "contract1_number_hours": contract1_number_hours,
                "contract1_counter_name": "Maintenance",
                "contract1_date": datetime.date.today(),
                "contract2_visible": contract2_visible,
                "contract2_total_type": contract2_total_type,
                "contract2_number_hours": contract2_number_hours,
                "contract2_counter_name": "Support",
                "contract2_date": datetime.date.today(),
                "contract3_visible": contract3_visible,
                "contract3_total_type": contract3_total_type,
                "contract3_number_hours": contract3_number_hours,
                "contract3_counter_name": "Corrective",
                "contract3_date": datetime.date.today(),
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
        cls.company, _, _, _ = create_project()

        cls.form_url = reverse("high_ui:update_project", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data_maintenance_types(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = ProjectUpdateView()
        view.request = request
        view.user = self.user
        view.company = self.company

        context = view.get_context_data()
        self.assertEqual(3, len(context["maintenance_types"]))

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_update_a_project(self):
        operator = OperatorUserFactory(first_name="Chell")
        company_name = "Aperture Science"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url,
            {
                "company_name": company_name,
                "contact": operator.pk,
                "contract1_visible": contract1_visible,
                "contract1_total_type": contract1_total_type,
                "contract1_number_hours": contract1_number_hours,
                "contract1_counter_name": "Maintenance",
                "contract1_date": datetime.date.today(),
                "contract2_visible": contract2_visible,
                "contract2_total_type": contract2_total_type,
                "contract2_number_hours": contract2_number_hours,
                "contract2_counter_name": "Support",
                "contract2_date": datetime.date.today(),
                "contract3_visible": contract3_visible,
                "contract3_total_type": contract3_total_type,
                "contract3_number_hours": contract3_number_hours,
                "contract3_counter_name": "Corrective",
                "contract3_date": datetime.date.today(),
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertTrue(Company.objects.get(name=company_name, pk=self.company.pk))
        contracts = MaintenanceContract.objects.filter(company_id=self.company.id)
        self.assertEqual(3, contracts.count())


class ProjectDetailsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, cls.contract, _, _ = create_project()
        cls.form_url = reverse("high_ui:project_details", args=[cls.company.slug_name])
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_can_seen_his_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_seen_his_company(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_seen_other_company(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_seen_a_company(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_add_credit_button(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Commander des heures")

    def test_display_extra_credit(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        MaintenanceCreditFactory(contract=self.contract, company=self.company, hours_number=10, date=now().date())

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="history-item-duration duration">+10h</td>')


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


class GetContextDataProjectDetailsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.months_nb = 6

    def test_last_months_in_the_middle_of_the_year(self):
        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2018, 6, 1))

        self.assertEqual(self.months_nb, len(months))

        self.assertEqual("06/18", months[0].strftime("%m/%y"))
        self.assertEqual("05/18", months[1].strftime("%m/%y"))
        self.assertEqual("04/18", months[2].strftime("%m/%y"))
        self.assertEqual("03/18", months[3].strftime("%m/%y"))
        self.assertEqual("02/18", months[4].strftime("%m/%y"))
        self.assertEqual("01/18", months[5].strftime("%m/%y"))

    def test_last_months_at_the_beginning_of_the_year(self):
        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2018, 2, 1))

        self.assertEqual(self.months_nb, len(months))

        self.assertEqual("02/18", months[0].strftime("%m/%y"))
        self.assertEqual("01/18", months[1].strftime("%m/%y"))
        self.assertEqual("12/17", months[2].strftime("%m/%y"))
        self.assertEqual("11/17", months[3].strftime("%m/%y"))
        self.assertEqual("10/17", months[4].strftime("%m/%y"))
        self.assertEqual("09/17", months[5].strftime("%m/%y"))

    def test_last_months_at_the_end_of_a_month(self):
        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2018, 12, 31))

        self.assertEqual(self.months_nb, len(months))

        self.assertEqual("12/18", months[0].strftime("%m/%y"))
        self.assertEqual("11/18", months[1].strftime("%m/%y"))
        self.assertEqual("10/18", months[2].strftime("%m/%y"))
        self.assertEqual("09/18", months[3].strftime("%m/%y"))
        self.assertEqual("08/18", months[4].strftime("%m/%y"))
        self.assertEqual("07/18", months[5].strftime("%m/%y"))

    def test_last_months_at_the_end_of_february(self):
        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2018, 2, 28))

        self.assertEqual(self.months_nb, len(months))

        self.assertEqual("02/18", months[0].strftime("%m/%y"))
        self.assertEqual("01/18", months[1].strftime("%m/%y"))
        self.assertEqual("12/17", months[2].strftime("%m/%y"))
        self.assertEqual("11/17", months[3].strftime("%m/%y"))
        self.assertEqual("10/17", months[4].strftime("%m/%y"))
        self.assertEqual("09/17", months[5].strftime("%m/%y"))

    def test_last_months_at_the_end_of_february_leap_year(self):
        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2020, 2, 29))

        self.assertEqual(self.months_nb, len(months))

        self.assertEqual("02/20", months[0].strftime("%m/%y"))
        self.assertEqual("01/20", months[1].strftime("%m/%y"))
        self.assertEqual("12/19", months[2].strftime("%m/%y"))
        self.assertEqual("11/19", months[3].strftime("%m/%y"))
        self.assertEqual("10/19", months[4].strftime("%m/%y"))
        self.assertEqual("09/19", months[5].strftime("%m/%y"))

    def test_get_contract_month_info(self):
        company, contract, _, _ = create_project(contract1={"start": datetime.date(2020, 2, 29)})
        MaintenanceIssueFactory(company=company, contract=contract, number_minutes=12, date=datetime.date(2020, 2, 29))
        month = datetime.date(2020, 2, 29)

        view = ProjectDetailsView()
        contract_info = view.get_contract_month_informations(month, contract)
        self.assertEqual((contract, 12, 20), contract_info)

    def test_get_contracts_month_info(self):
        company, _, _, _ = create_project(contract1={"start": datetime.date(2020, 2, 29)})
        month = datetime.date(2020, 2, 29)
        contracts = MaintenanceContract.objects.filter(company=company)

        view = ProjectDetailsView()
        contracts_info = view.get_contracts_month_informations(month, contracts)
        self.assertEqual(3, len(contracts_info))

    def test_get_activities(self):
        company, _, _, _ = create_project(contract1={"start": datetime.date(2020, 2, 29)})
        contracts = MaintenanceContract.objects.filter(company=company)

        view = ProjectDetailsView()
        months = view.get_last_months(datetime.date(2020, 2, 29))
        activities = view.get_activities(months, contracts)
        self.assertEqual(6, len(activities))

    def test_get_maintenance_issues(self):
        company, contract1, contract2, contract3 = create_project(
            contract1={"start": datetime.date(2020, 2, 29)}, contract2={"disabled": True}, contract3={"visible": False}
        )
        month = datetime.date(2020, 2, 29)
        MaintenanceIssueFactory(company=company, contract=contract1, number_minutes=12, date=datetime.date(2020, 2, 29))
        MaintenanceIssueFactory(company=company, contract=contract1, number_minutes=12, date=datetime.date(2018, 2, 28))
        MaintenanceIssueFactory(company=company, contract=contract2, number_minutes=12, date=datetime.date(2020, 2, 29))
        MaintenanceIssueFactory(company=company, contract=contract3, number_minutes=12, date=datetime.date(2020, 2, 29))

        view = ProjectDetailsView()
        view.company = company

        contracts = MaintenanceContract.objects.filter(company=company, disabled=False)
        issues = view.get_maintenance_issues(month, contracts)

        self.assertEqual(2, len(issues))

    def test_get_maintenance_credits(self):
        company, contract1, contract2, contract3 = create_project(
            contract1={"start": datetime.date(2020, 2, 29)}, contract2={"disabled": True}, contract3={"visible": False}
        )
        month = datetime.date(2020, 2, 29)
        MaintenanceCreditFactory(company=company, contract=contract1, hours_number=12, date=datetime.date(2020, 2, 29))
        MaintenanceCreditFactory(company=company, contract=contract1, hours_number=12, date=datetime.date(2018, 2, 28))
        MaintenanceCreditFactory(company=company, contract=contract2, hours_number=12, date=datetime.date(2020, 2, 29))
        MaintenanceCreditFactory(company=company, contract=contract3, hours_number=12, date=datetime.date(2020, 2, 29))

        view = ProjectDetailsView()
        view.company = company

        contracts = MaintenanceContract.objects.filter(company=company, disabled=False)
        credits = view.get_maintenance_credits(month, contracts)

        self.assertEqual(2, len(credits))

    def test_get_ordered_issues_and_credits(self):
        company, contract1, _, _ = create_project(contract1={"start": datetime.date(2020, 2, 29)})
        month = datetime.date(2020, 2, 29)
        MaintenanceIssueFactory(company=company, contract=contract1, date=datetime.date(2020, 2, 28))
        MaintenanceCreditFactory(company=company, contract=contract1, date=datetime.date(2020, 2, 27))
        MaintenanceCreditFactory(company=company, contract=contract1, date=datetime.date(2020, 2, 29))

        view = ProjectDetailsView()
        view.company = company

        contracts = MaintenanceContract.objects.filter(company=company, disabled=False)
        events = view.get_ordered_issues_and_credits(month, contracts)

        self.assertEqual(1, events[0])
        self.assertEqual("credit", events[1][0]["type"])
        self.assertEqual(datetime.date(2020, 2, 29), events[1][0]["date"])
        self.assertEqual("issue", events[1][1]["type"])
        self.assertEqual(datetime.date(2020, 2, 28), events[1][1]["date"])
        self.assertEqual("credit", events[1][2]["type"])
        self.assertEqual(datetime.date(2020, 2, 27), events[1][2]["date"])

    def test_get_history(self):
        months_nb = 6
        company, c1, c2, c3 = create_project(
            contract1={"start": datetime.date(2020, 2, 29)}, contract2={"disabled": True}, contract3={"visible": False}
        )
        MaintenanceIssueFactory(company=company, contract=c1, number_minutes=12, date=datetime.date(2020, 2, 29))
        MaintenanceIssueFactory(company=company, contract=c1, number_minutes=12, date=datetime.date(2018, 2, 28))
        MaintenanceIssueFactory(company=company, contract=c2, number_minutes=12, date=datetime.date(2020, 2, 29))
        MaintenanceIssueFactory(company=company, contract=c3, number_minutes=12, date=datetime.date(2020, 2, 29))
        contracts = MaintenanceContract.objects.filter(company=company, disabled=False)

        view = ProjectDetailsView()
        view.company = company

        months = view.get_last_months(datetime.date(2020, 2, 29))
        history = view.get_history(months, contracts)

        self.assertEqual(months_nb, len(history))
        self.assertEqual(2, len(history[0][2]))  # how many issues in the first month

    def test_get_context_data(self):
        company, c1, c2, c3 = create_project(
            contract1={"start": datetime.date(2020, 2, 29)}, contract2={"disabled": True}, contract3={"visible": False}
        )
        form_url = reverse("high_ui:project_details", args=[company.slug_name])
        factory = RequestFactory()
        request = factory.get(form_url)

        user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        request.user = user
        view = ProjectDetailsView()
        view.request = request
        view.user = user
        view.object = company
        view.company = company

        context = view.get_context_data()
        self.assertIn("activities", context.keys())
        self.assertEqual(6, len(context["activities"]))
        self.assertIn("history", context.keys())
        self.assertEqual(6, len(context["history"]))
