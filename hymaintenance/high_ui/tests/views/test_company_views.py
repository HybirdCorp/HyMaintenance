
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.models import Company
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from high_ui.views import CompanyDetailView
from maintenance.models.contract import MaintenanceContract
from maintenance.tests.factories import MaintenanceIssueFactory, MaintenanceTypeFactory


class CreateCompanyViewTestCase(TestCase):
    def test_create_company_with_form(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        name = "Black Mesa GG-3883 Experiment"
        maintenance_contact = "Gordon F."

        response = client.post('/high_ui/company/add/',
                               {"name": name,
                                "maintenance_contact": maintenance_contact}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Company.objects.filter(name=name, maintenance_contact=maintenance_contact).count())


class CompanyDetailViewTestCase(TestCase):
    def test_user_can_seen_this_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[first_company.pk]))

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_seen_other_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        black_mesa = CompanyFactory()
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[black_mesa.pk]))

        self.assertEqual(response.status_code, 404)


def create_mtype_maintenance_and_issue(visible, company):
        maintenance_type = MaintenanceTypeFactory(visible=visible)
        MaintenanceContract.objects.create(company=company,
                                           start=now().date(),
                                           maintenance_type=maintenance_type,
                                           number_hours=40)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                number_minutes=12)


class VisibleMaintenanceTypeContractTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_company_detail_view_with_request(self, user, companypk):
        request = self.factory.get(reverse('high_ui:company-details', args=[companypk]))
        request.user = user
        view = CompanyDetailView()
        view.request = request
        return view

    def test_user_cannot_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(0, contracts.count())

    def test_manageruser_can_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_user_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())

    def test_manageruser_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        contracts = view.get_maintenance_contracts(self.company)
        self.assertEqual(1, contracts.count())


class VisibleMaintenanceTypeIssueTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.factory = RequestFactory()

    def create_company_detail_view_with_request(self, user, companypk):
        request = self.factory.get(reverse('high_ui:company-details', args=[companypk]))
        request.user = user
        view = CompanyDetailView()
        view.request = request
        return view

    def test_user_cannot_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(0, issues.count())

    def test_manageruser_can_see_invisible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(False, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_user_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty",
                                      company=self.company)
        create_mtype_maintenance_and_issue(True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())

    def test_manageruser_can_see_visible(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        create_mtype_maintenance_and_issue(True, self.company)
        view = self.create_company_detail_view_with_request(user, self.company.pk)
        issues = view.get_maintenance_issues(self.company, now().date())
        self.assertEqual(1, issues.count())
