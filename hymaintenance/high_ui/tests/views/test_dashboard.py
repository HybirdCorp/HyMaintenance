from customers.tests.factories import AdminOperatorUserFactory
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from ...views.dashboard import DashboardView


class DashboardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory(name="Aperture Science")
        cls.page_url = reverse("high_ui:dashboard")
        cls.login_url = reverse("login") + "?next=" + cls.page_url

    def test_get_context_data_companies_number_for_admin(self):
        user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        CompanyFactory(is_archived=True)

        factory = RequestFactory()
        request = factory.get(self.page_url)
        request.user = user
        view = DashboardView()
        view.request = request
        view.user = user

        context = view.get_context_data()
        self.assertEqual(1, context["companies_number"])

    def test_get_context_data_companies_number_for_operator(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)
        archived_company = CompanyFactory(is_archived=True)
        user.operator_for.add(archived_company)
        CompanyFactory()

        factory = RequestFactory()
        request = factory.get(self.page_url)
        request.user = user
        view = DashboardView()
        view.request = request
        view.user = user

        context = view.get_context_data()
        self.assertEqual(1, context["companies_number"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_seen_the_dashboard(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        user.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_the_dashboard(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.company.get_absolute_url())

    def test_operator_user_can_seen_this_company(self):
        OperatorUserFactory(email="other.man@blackmesa.com", password="azerty", first_name="Op1", last_name="Op1")
        op2 = OperatorUserFactory(
            email="gordon.freeman@blackmesa.com", password="azerty", first_name="Op2", last_name="Op2"
        )
        op2.operator_for.add(self.company)
        archive_company = CompanyFactory(name="Aperture Fixtures", is_archived=True)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(1, self.company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Op2 Op2")
        self.assertNotContains(response, "Op1 Op1")
        self.assertNotContains(response, archive_company.name)

    def test_operator_admin_user_can_seen_all_companies(self):
        admin = AdminOperatorUserFactory(email="other.man@blackmesa.com", password="azerty")
        other_company = CompanyFactory(name="Black Mesa")
        archive_company = CompanyFactory(name="Aperture Fixtures", is_archived=True)

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(0, other_company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.company.name)
        self.assertContains(response, other_company.name)
        self.assertNotContains(response, archive_company.name)

    def test_admin_user_can_seen_all_active_companies(self):
        admin = AdminUserFactory(email="other.man@blackmesa.com", password="azerty")
        other_company = CompanyFactory(name="Black Mesa")
        archive_company = CompanyFactory(name="Aperture Fixtures", is_archived=True)

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(0, other_company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.company.name)
        self.assertContains(response, other_company.name)
        self.assertNotContains(response, archive_company.name)
