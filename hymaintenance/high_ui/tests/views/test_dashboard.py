
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, OperatorUserFactory
from maintenance.tests.factories import MaintenanceUserFactory


class DashboardTestCase(TestCase):

    def setUp(self):
        self.company = CompanyFactory()

    def test_operator_can_seen_the_dashboard(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:home'))

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_the_dashboard(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:home'))

        self.assertRedirects(response, self.company.get_absolute_url())

    def test_operator_user_can_seen_this_company(self):
        OperatorUserFactory(email="other.man@blackmesa.com", password="azerty", first_name="Op1",
                            last_name="Op1")
        op2 = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", first_name="Op2",
                                  last_name="Op2")
        op2.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:home'))

        self.assertEqual(1, self.company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Op2 Op2")
        self.assertNotContains(response, "Op1 Op1")
