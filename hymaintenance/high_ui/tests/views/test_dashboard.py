
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory
from maintenance.tests.factories import MaintenanceUserFactory


class DashboardTestCase(TestCase):

    def test_operator_can_seen_the_dashboard(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:home'))

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_the_dashboard(self):
        company = CompanyFactory(name="Black Mesa")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=company)
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:home'))

        self.assertRedirects(response, company.get_absolute_url())
