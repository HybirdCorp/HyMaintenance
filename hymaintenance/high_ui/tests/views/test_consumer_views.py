
from django.test import Client, TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceConsumer


class CreateConsumerViewTestCase(TestCase):

    def test_create_maintenance_consumer_with_form(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        company = CompanyFactory()

        name = "New consumer name for company %s" % company.pk
        assert len(name) < 255

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.post('/high_ui/consumer/add/%s/' % company.pk, {"name": name}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceConsumer.objects.filter(company=company, name=name).count())
