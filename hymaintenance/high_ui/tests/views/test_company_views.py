from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, ManagerUserFactory, OperatorUserFactory
from high_ui.views.company import ProjectDetailsView
from maintenance.models import MaintenanceContract
from maintenance.tests.factories import MaintenanceContractFactory, MaintenanceIssueFactory, get_default_maintenance_type


class ProjectDetailsViewTestCase(TestCase):

    def test_when_the_company_does_not_exist(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:project_details', args=[1]))

        self.assertEqual(response.status_code, 404)

    def test_manager_user_can_seen_this_company(self):
        first_company = CompanyFactory(name="First Company")
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:project_details', args=[first_company.slug_name]))

        self.assertEqual(response.status_code, 200)

    def test_customer_user_cannot_seen_other_company(self):
        first_company = CompanyFactory(name="First Company")
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        black_mesa = CompanyFactory()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:project_details', args=[black_mesa.slug_name]))

        self.assertEqual(response.status_code, 404)

    def test_operator_user_cannot_seen_other_company(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        black_mesa = CompanyFactory()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:project_details', args=[black_mesa.slug_name]))

        self.assertEqual(response.status_code, 404)


def create_mtype_maintenance_and_issue(maintenance_type_visibility, contract_visibility, company):
        maintenance_type = get_default_maintenance_type()
        maintenance_type.visibility = maintenance_type_visibility
        MaintenanceContract.objects.create(company=company,
                                           start=now().date(),
                                           maintenance_type=maintenance_type,
                                           visible=contract_visibility,
                                           number_hours=40)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                number_minutes=12)


class MonthDisplayInFrenchTestCase(TestCase):
    def test_month_display_in_french(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        company = CompanyFactory()
        user.operator_for.add(company)
        MaintenanceContractFactory(company=company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(reverse('high_ui:project_details', args=[company.slug_name]))

        month = now().date().month
        frenchmonths = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "décembre"]

        self.assertContains(response, frenchmonths[month - 1])


class ContractVisibilityTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_project_details_view_with_request(self, user, company_slug_name):
        request = self.factory.get(reverse('high_ui:project_details', args=[company_slug_name]))
        request.user = user
        view = ProjectDetailsView()
        view.request = request
        return view

    def test_manager_user_cannot_see_invisible(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(0, contracts.count())

    def test_manager_user_can_see_visible(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_manager_user_cannot_see_invisible_in_contract(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(0, contracts.count())

    def test_manager_user_can_see_visible_in_contract(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_user_can_see_invisible(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_user_can_see_visible(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_user_can_see_invisible_in_contract(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_user_can_see_visible_in_contract(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())


class IssueVisibilityTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_project_details_view_with_request(self, user, company_slug_name):
        request = self.factory.get(reverse('high_ui:project_details', args=[company_slug_name]))
        request.user = user
        view = ProjectDetailsView()
        view.request = request
        return view

    def test_manager_user_cannot_see_invisible(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(0, issues.count())

    def test_manager_user_can_see_visible(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_manager_user_cannot_see_invisible_in_contract(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(0, issues.count())

    def test_manager_user_can_see_visible_in_contract(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                                  password="azerty",
                                  company=self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_user_can_see_invisible(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_user_can_see_visible(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_user_can_see_invisible_in_contract(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_user_can_see_visible_in_contract(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_project_details_view_with_request(user, self.company.slug_name)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())
