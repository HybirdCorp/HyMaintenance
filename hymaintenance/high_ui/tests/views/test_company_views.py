from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from high_ui.views import CompanyDetailView
from maintenance.models import MaintenanceContract
from maintenance.tests.factories import MaintenanceContractFactory, MaintenanceIssueFactory, get_default_maintenance_type


class CompanyDetailViewTestCase(TestCase):
    def test_customer_user_can_seen_this_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[first_company.pk]))

        self.assertEqual(response.status_code, 200)

    def test_customer_user_cannot_seen_other_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        black_mesa = CompanyFactory()
        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[black_mesa.pk]))

        self.assertEqual(response.status_code, 404)

    def test_operator_user_cannot_seen_other_company(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        black_mesa = CompanyFactory()
        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[black_mesa.pk]))

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
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        company = CompanyFactory()
        user.operator_for.add(company)
        MaintenanceContractFactory(company=company)

        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.get(reverse('high_ui:company-details', args=[company.pk]))

        month = now().date().month
        frenchmonths = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "décembre"]

        self.assertContains(response, frenchmonths[month - 1])


class ContractVisibilityTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_company_detail_view_with_request(self, user, companypk):
        request = self.factory.get(reverse('high_ui:company-details', args=[companypk]))
        request.user = user
        view = CompanyDetailView()
        view.request = request
        return view

    def test_customer_user_cannot_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(0, contracts.count())

    def test_customer_user_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_customer_user_cannot_see_invisible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(0, contracts.count())

    def test_customer_user_can_see_visible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_can_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_can_see_invisible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_operator_can_see_visible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())


class IssueVisibilityTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_company_detail_view_with_request(self, user, companypk):
        request = self.factory.get(reverse('high_ui:company-details', args=[companypk]))
        request.user = user
        view = CompanyDetailView()
        view.request = request
        return view

    def test_customer_user_cannot_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(0, issues.count())

    def test_customer_user_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_customer_user_cannot_see_invisible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(0, issues.count())

    def test_customer_user_can_see_visible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_can_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_can_see_invisible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_operator_can_see_visible_in_contract(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())
