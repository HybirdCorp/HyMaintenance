
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminOperatorUserFactory
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory


class DashboardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory(name="Aperture Science")
        cls.page_url = reverse("high_ui:dashboard")

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

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(1, self.company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Op2 Op2")
        self.assertNotContains(response, "Op1 Op1")

    def test_operator_admin_user_can_seen_all_companies(self):
        admin = AdminOperatorUserFactory(email="other.man@blackmesa.com", password="azerty")
        other_company = CompanyFactory(name="Black Mesa")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(0, other_company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.company.name)
        self.assertContains(response, other_company.name)

    def test_admin_user_can_seen_all_companies(self):
        admin = AdminUserFactory(email="other.man@blackmesa.com", password="azerty")
        other_company = CompanyFactory(name="Black Mesa")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(0, other_company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.company.name)
        self.assertContains(response, other_company.name)
